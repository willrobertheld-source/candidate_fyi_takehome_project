from django.contrib import admin

from .models import InterviewTemplate, Interviewer


@admin.register(Interviewer)
class InterviewerAdmin(admin.ModelAdmin):
    list_display = ["id", "name"]
    search_fields = ["name"]


@admin.register(InterviewTemplate)
class InterviewTemplateAdmin(admin.ModelAdmin):
    list_display = ["id", "name", "duration_minutes"]
    search_fields = ["name"]
    filter_horizontal = ["interviewers"]
