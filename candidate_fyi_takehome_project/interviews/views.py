from datetime import datetime, timedelta, timezone

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from services.mock_availability import get_free_busy_data

from .models import InterviewTemplate

WORK_START_HOUR = 9
WORK_END_HOUR = 17
SEARCH_DAYS = 8


def _parse_dt(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def _merge_busy_blocks(blocks: list[tuple]) -> list[tuple]:
    """Sort and merge overlapping or adjacent busy intervals.

    External calendar data may return overlapping blocks for the same person
    (e.g. a recurring meeting that coincides with a one-off event). Without
    merging, the complement calculation would produce spurious free windows
    inside the overlap, leading to slots being offered when the interviewer
    is actually busy.
    """
    if not blocks:
        return []
    sorted_blocks = sorted(blocks, key=lambda x: x[0])
    merged: list[list] = [list(sorted_blocks[0])]
    for start, end in sorted_blocks[1:]:
        if start <= merged[-1][1]:
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [tuple(b) for b in merged]  # type: ignore[misc]


def _subtract_busy(interval_start: datetime, interval_end: datetime, busy: list[tuple]) -> list[tuple]:
    """Return free sub-intervals within [interval_start, interval_end] after removing busy blocks."""
    free = []
    cursor = interval_start
    for busy_start, busy_end in busy:
        if busy_end <= cursor:
            continue
        if busy_start >= interval_end:
            break
        if busy_start > cursor:
            free.append((cursor, min(busy_start, interval_end)))
        cursor = max(cursor, busy_end)
    if cursor < interval_end:
        free.append((cursor, interval_end))
    return free


def _intersect(list_a: list[tuple], list_b: list[tuple]) -> list[tuple]:
    """Compute intersection of two sorted, non-overlapping interval lists."""
    result = []
    i = j = 0
    while i < len(list_a) and j < len(list_b):
        start = max(list_a[i][0], list_b[j][0])
        end = min(list_a[i][1], list_b[j][1])
        if start < end:
            result.append((start, end))
        if list_a[i][1] < list_b[j][1]:
            i += 1
        else:
            j += 1
    return result


def _snap_to_next_half_hour(dt: datetime) -> datetime:
    """Return the earliest :00 or :30 timestamp that is >= dt."""
    dt = dt.replace(second=0, microsecond=0)
    if dt.minute == 0:
        return dt
    if dt.minute <= 30:
        return dt.replace(minute=30)
    return (dt + timedelta(hours=1)).replace(minute=0)


def _slots_in_interval(
    free_start: datetime,
    free_end: datetime,
    duration: timedelta,
    earliest_start: datetime,
) -> list[dict]:
    slots = []
    candidate = _snap_to_next_half_hour(free_start)
    step = timedelta(minutes=30)
    while candidate + duration <= free_end:
        if candidate >= earliest_start:
            slots.append(
                {
                    "start": candidate.strftime("%Y-%m-%dT%H:%M:%SZ"),
                    "end": (candidate + duration).strftime("%Y-%m-%dT%H:%M:%SZ"),
                }
            )
        candidate += step
    return slots


class InterviewAvailabilityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, interview_id):
        try:
            template = InterviewTemplate.objects.prefetch_related("interviewers").get(pk=interview_id)
        except InterviewTemplate.DoesNotExist:
            return Response({"error": "Interview template not found."}, status=404)

        interviewers = list(template.interviewers.all())
        if not interviewers:
            return Response(
                {
                    "interviewId": template.id,
                    "name": template.name,
                    "durationMinutes": template.duration_minutes,
                    "interviewers": [],
                    "availableSlots": [],
                }
            )

        now = datetime.now(timezone.utc)
        earliest_slot_start = now + timedelta(hours=24)
        search_end = now + timedelta(days=SEARCH_DAYS)

        interviewer_ids = [i.id for i in interviewers]
        busy_data = get_free_busy_data(interviewer_ids)

        # Build merged busy-block map keyed by the interviewer DB id.
        # The mock service returns entries in the same order as the IDs passed in,
        # so we zip by position to avoid fragile name matching.
        busy_map: dict[int, list[tuple]] = {}
        for iid, entry in zip(interviewer_ids, busy_data):
            raw = [(_parse_dt(b["start"]), _parse_dt(b["end"])) for b in entry["busy"]]
            busy_map[iid] = _merge_busy_blocks(raw)

        # For each interviewer compute free intervals restricted to working hours.
        all_free: list[list[tuple]] = []
        for iid in interviewer_ids:
            busy = busy_map.get(iid, [])
            free_intervals: list[tuple] = []

            current_date = earliest_slot_start.date()
            end_date = search_end.date()
            while current_date <= end_date:
                work_start = datetime(
                    current_date.year, current_date.month, current_date.day,
                    WORK_START_HOUR, 0, tzinfo=timezone.utc,
                )
                work_end = datetime(
                    current_date.year, current_date.month, current_date.day,
                    WORK_END_HOUR, 0, tzinfo=timezone.utc,
                )
                # Clip to the actual search window.
                work_start = max(work_start, earliest_slot_start)
                work_end = min(work_end, search_end)

                if work_start < work_end:
                    free_intervals.extend(_subtract_busy(work_start, work_end, busy))

                current_date += timedelta(days=1)

            all_free.append(free_intervals)

        # Intersect free intervals across all interviewers.
        combined_free = all_free[0]
        for free_list in all_free[1:]:
            combined_free = _intersect(combined_free, free_list)

        # Generate slots at :00/:30 marks within jointly-free intervals.
        duration = timedelta(minutes=template.duration_minutes)
        available_slots: list[dict] = []
        for free_start, free_end in combined_free:
            available_slots.extend(
                _slots_in_interval(free_start, free_end, duration, earliest_slot_start)
            )

        return Response(
            {
                "interviewId": template.id,
                "name": template.name,
                "durationMinutes": template.duration_minutes,
                "interviewers": [{"id": i.id, "name": i.name} for i in interviewers],
                "availableSlots": available_slots,
            }
        )
