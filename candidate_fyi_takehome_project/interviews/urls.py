from django.urls import path

from .views import InterviewAvailabilityView

urlpatterns = [
    path("<int:interview_id>/availability", InterviewAvailabilityView.as_view(), name="interview-availability"),
]
