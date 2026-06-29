from django.db import models


class Interviewer(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class InterviewTemplate(models.Model):
    name = models.CharField(max_length=255)
    duration_minutes = models.PositiveIntegerField()
    interviewers = models.ManyToManyField(
        Interviewer,
        related_name="interview_templates",
        blank=True,
    )

    def __str__(self):
        return f"{self.name} ({self.duration_minutes} min)"
