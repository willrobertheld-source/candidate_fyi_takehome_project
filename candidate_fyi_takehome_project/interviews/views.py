from datetime import datetime, timezone

from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView

from services.mock_availability import get_free_busy_data

from .services import compute_available_slots
from .models import InterviewTemplate
from .serializers import InterviewAvailabilitySerializer


class InterviewAvailabilityView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, interview_id):
        try:
            template = InterviewTemplate.objects.prefetch_related("interviewers").get(pk=interview_id)
        except InterviewTemplate.DoesNotExist:
            return Response({"error": "Interview template not found."}, status=404)

        interviewers = list(template.interviewers.all())
        if not interviewers:
            serializer = InterviewAvailabilitySerializer(template, context={"available_slots": []})
            return Response(serializer.data)

        interviewer_ids = [i.id for i in interviewers]
        busy_data = get_free_busy_data(interviewer_ids)

        available_slots = compute_available_slots(
            interviewer_ids=interviewer_ids,
            busy_data=busy_data,
            duration_minutes=template.duration_minutes,
            now=datetime.now(timezone.utc),
        )

        serializer = InterviewAvailabilitySerializer(template, context={"available_slots": available_slots})
        return Response(serializer.data)
