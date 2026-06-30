# 🧠 Backend Take-Home: **Dynamic Interview Slot Generator (Django)**

## 🗂️ Overview

In this take-home challenge, you'll implement a backend feature for a scheduling tool like [candidate.fyi](https://candidate.fyi/). The goal is to **dynamically generate potential interview time slots** by intersecting the real-time availability of multiple interviewers.

Unlike systems with static slots, this exercise simulates a more realistic setup — pulling external calendar data, evaluating overlapping availability, and applying constraints.

---

## 🎯 Goal

Build an API that, given an interview template ID, returns potential time slots where **all assigned interviewers are available at the same time** for the required duration.

---

## 🛠️ Tech Stack

You must use:

- Python 3.10+
- Django 4.x
- Django REST Framework (DRF)
- SQLite or PostgreSQL
- Faker (already used in provided helper)

---

## 📋 Core Requirements

### ✅ Models

You'll need to implement models to support this feature. At a minimum:

- `Interviewer`: represents someone who conducts interviews
- `InterviewTemplate`: represents a type of interview, with:
    - A name (e.g., "Technical Interview")
    - A duration in minutes (e.g., 60)
    - A many-to-many relationship to Interviewers

You're free to design additional models if it helps with clarity or flexibility.

---

### ✅ Endpoint

```bash
GET /api/interviews/<id>/availability
```

This endpoint should:

1. Load the `InterviewTemplate` with the given ID
2. Use the **provided mock service** to fetch availability for all associated interviewers
3. Return **only time slots where all interviewers are simultaneously available** for the required duration
4. Format the result as a JSON response

---

## 🧾 Interviewer Availability Service

To simulate the external calendar system, use the helper in:

```
service/mock_availability.py
```

Import and call the function like so:

```python
from service.mock_availability import get_free_busy_data

interviewer_ids = [1, 2]
busy_data = get_free_busy_data(interviewer_ids)

```

### 🔄 Sample Output

```json
[
  {
    "interviewerId": 1,
    "name": "Alice Johnson",
    "busy": [
      { "start": "2025-01-22T09:00:00Z", "end": "2025-01-22T12:00:00Z" }
    ]
  },
  {
    "interviewerId": 2,
    "name": "Bob Smith",
    "busy": [
      { "start": "2025-01-22T10:00:00Z", "end": "2025-01-22T13:00:00Z" }
    ]
  }
]
```

> ✅ You are welcome to enhance or modify this service as needed — e.g., to support filtering, partial day simulation, or sorting.

---

## 📤 API Response Format

```json
{
  "interviewId": 1,
  "name": "Technical Interview",
  "durationMinutes": 60,
  "interviewers": [
    { "id": 1, "name": "Alice Johnson" },
    { "id": 2, "name": "Bob Smith" }
  ],
  "availableSlots": [
    {
      "start": "2025-01-22T10:00:00Z",
      "end": "2025-01-22T11:00:00Z"
    },
    {
      "start": "2025-01-22T11:00:00Z",
      "end": "2025-01-22T12:00:00Z"
    }
  ]
}
```

---

## ⚠️ Constraints

You must enforce the following:

- Slots must be **exactly** the duration minutes of the template
- Slots must begin on **hour or half-hour marks** (e.g., 10:00, 10:30)
- **All interviewers must be available** for the full slot duration
- **No slot may begin less than 24 hours** in the future
- All times must be in **UTC** in ISO 8601 format

---

### 🧠 Developer Insight (Required)

In addition to meeting the requirements above, we'd like you to demonstrate how you think beyond the surface.

### ✅ What to Do:

As part of your submission, please identify **one unique edge case or complexity** you encountered that wasn't explicitly mentioned in the prompt.

- This could relate to availability overlaps, data inconsistencies, ambiguous logic, or system design.
- Implement your handling of it in the code.
- Add a short explanation in your README:
    - What the case was
    - Why it mattered
    - How you handled it

### 💡 Why:

In real-world systems, requirements evolve and edge cases emerge. We want to see how you anticipate and reason about those situations — not just follow a spec.

---

## 📦 Submission

Submit a GitHub repo with:

- All source code
- Your own models, views, serializers
- README with:
    - Setup instructions
    - Design decisions
    - Your extra edge case write-up

---

## 🚀 Running the Application

### Option 1: Using Docker (Recommended)

This project includes Docker configuration for easy setup and consistent environments.

1. **Make sure Docker and Docker Compose are installed on your system**

2. **Build and start the application**
   ```bash
   # Build and start all services
   make up
   
   # Or alternatively
   docker-compose up -d
   ```

3. **Run migrations**
   ```bash
   make migrate
   
   # Or alternatively
   docker-compose exec web python manage.py migrate
   ```

4. **Create a superuser (optional)**
   ```bash
   make superuser
   
   # Or alternatively
   docker-compose exec web python manage.py createsuperuser
   ```

5. **Load sample data (optional)**
   ```bash
   make loaddata
   
   # Or alternatively
   docker-compose exec web python manage.py loaddata sample_data
   ```

6. **Access the API**
   
   The API will be available at: http://localhost:8000/api/interviews/<id>/availability

### Other Useful Commands

```bash
# View logs
make logs

# Run tests
make test

# Stop all containers
make down

# Shell into web container
make shell
```

### Option 2: Local Setup

If you prefer running the application without Docker:

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd <repository-directory>
   ```

2. **Create and activate a virtual environment**
   ```bash
   python -m venv venv
   
   # On Windows
   venv\Scripts\activate
   
   # On macOS/Linux
   source venv/bin/activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Apply migrations**
   ```bash
   python manage.py migrate
   ```

5. **Run the development server**
   ```bash
   python manage.py runserver
   ```

---

## 🗂️ Design Decisions

### App structure
All new code lives in a dedicated `candidate_fyi_takehome_project/interviews/` Django app:

| File | Purpose |
|---|---|
| `models.py` | `Interviewer` and `InterviewTemplate` models |
| `services.py` | All interval arithmetic: merging, subtracting, intersecting, slot generation |
| `serializers.py` | DRF serializers for response shaping |
| `views.py` | HTTP layer only — delegates logic to `services.py` and `serializers.py` |
| `urls.py` | Routes `<int:interview_id>/availability` to the view |
| `admin.py` | Django admin registration for both models |
| `migrations/` | Hand-written initial migration |

This keeps the feature self-contained and consistent with the existing `users` app pattern.

### Models
- **`Interviewer`** — minimal model with just `id` and `name`. In a production system this would link to the `User` model, but the mock service only needs an integer ID, so keeping it simple avoids unnecessary coupling.
- **`InterviewTemplate`** — holds `name`, `duration_minutes`, and a M2M to `Interviewer`. The duration drives all slot-length enforcement; putting it on the template (not the slot) means a single template change propagates everywhere.

### Availability algorithm
1. Call `get_free_busy_data(interviewer_ids)` to get busy blocks for all interviewers.
2. **Merge overlapping busy blocks** per interviewer (see edge case below).
3. For each interviewer, subtract their busy blocks from 9 am–5 pm working windows across the next 8 days, producing a list of free intervals.
4. Intersect all interviewers' free-interval lists using a two-pointer sweep — O(n) per pair.
5. Walk each jointly-free window and emit slots at `:00`/`:30` marks where the full duration fits.
6. Enforce the 24-hour minimum lead time by clipping the working window start to `now + 24 h`.

### Working-hours constraint
The mock service generates busy blocks only within 9 am–5 pm UTC. Treating all other hours as "free" would produce valid-looking slots at 2 am or on Sunday nights. The implementation constrains slot search to the same 9–17 UTC band, which produces a realistic result and stays consistent with the mock data's intent.

### Serializers
Three DRF serializer classes handle response shaping:
- `InterviewerSerializer` (ModelSerializer) — id + name from the DB
- `AvailableSlotSerializer` (Serializer) — start/end strings for each computed slot
- `InterviewAvailabilitySerializer` (ModelSerializer) — assembles the full response; receives computed slots via `context` so the view stays responsible for business logic and the serializer stays responsible for output format.

### Authentication
The availability endpoint uses `AllowAny` so it can be tested without a session or token. In production this would be tightened to require authentication.

---

## 🧠 Developer Insight: Edge Case

### What the case was
The external calendar service can return **overlapping busy blocks for the same interviewer** — for example, a recurring weekly team meeting (10:00–11:00) and a one-off event added on top of it (10:30–12:00) both appear as separate entries in the busy list for the same person.

### Why it mattered
The free-time calculation works by subtracting busy blocks from a working window. If two blocks overlap and are processed naively (without first merging them), the algorithm sees a gap between the end of the first block and the start of the second — even though the person is still busy during that gap. This produces phantom free windows inside a period when the interviewer is actually occupied, causing slots to be offered that cannot actually be booked.

### How it was handled
Before any free-time arithmetic is done, `merge_busy_blocks()` in `interviews/services.py` sorts all busy blocks by start time and merges any that overlap or are adjacent into a single contiguous block. The merged list is then what gets subtracted from the working window, eliminating any spurious free gaps. This runs once per interviewer per request and is O(n log n) due to the sort.

```python
def merge_busy_blocks(blocks):
    sorted_blocks = sorted(blocks, key=lambda x: x[0])
    merged = [list(sorted_blocks[0])]
    for start, end in sorted_blocks[1:]:
        if start <= merged[-1][1]:          # overlap or adjacent
            merged[-1][1] = max(merged[-1][1], end)
        else:
            merged.append([start, end])
    return [tuple(b) for b in merged]
```

