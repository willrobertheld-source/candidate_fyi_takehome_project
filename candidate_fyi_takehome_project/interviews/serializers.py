from rest_framework import serializers

from .models import Interviewer, InterviewTemplate


class InterviewerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Interviewer
        fields = ["id", "name"]


class AvailableSlotSerializer(serializers.Serializer):
    start = serializers.CharField()
    end = serializers.CharField()


class InterviewAvailabilitySerializer(serializers.ModelSerializer):
    interviewId = serializers.IntegerField(source="id")
    durationMinutes = serializers.IntegerField(source="duration_minutes")
    interviewers = InterviewerSerializer(many=True, read_only=True)
    availableSlots = serializers.SerializerMethodField()

    class Meta:
        model = InterviewTemplate
        fields = ["interviewId", "name", "durationMinutes", "interviewers", "availableSlots"]

    def get_availableSlots(self, obj):
        slots = self.context.get("available_slots", [])
        return AvailableSlotSerializer(slots, many=True).data
