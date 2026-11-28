from rest_framework import serializers
from django.utils import timezone

from apps.stations.models import Station
from apps.stations.serializers import StationSerializer
from .models import BookingPlan, BookingReminder


class BookingReminderSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingReminder
        fields = ("id", "remind_at", "status", "sent_at", "created_at")
        read_only_fields = ("id", "status", "sent_at", "created_at")

    def validate_remind_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Choose a reminder time in the future.")
        return value


class BookingPlanSerializer(serializers.ModelSerializer):
    source_station = StationSerializer(read_only=True)
    destination_station = StationSerializer(read_only=True)
    source_code = serializers.SlugRelatedField(source="source_station", slug_field="code", queryset=Station.objects.filter(is_active=True), write_only=True)
    destination_code = serializers.SlugRelatedField(source="destination_station", slug_field="code", queryset=Station.objects.filter(is_active=True), write_only=True)
    reminders = BookingReminderSerializer(many=True, read_only=True)
    booking_handoff_url = serializers.SerializerMethodField()

    class Meta:
        model = BookingPlan
        fields = (
            "id", "label", "source_station", "destination_station", "source_code", "destination_code",
            "journey_date", "preferred_class", "quota", "booking_opens_at", "status", "reminders",
            "booking_handoff_url", "created_at",
        )
        read_only_fields = ("id", "status", "created_at")

    def get_booking_handoff_url(self, obj):
        return "https://www.irctc.co.in"

    def validate(self, attrs):
        source = attrs.get("source_station", getattr(self.instance, "source_station", None))
        destination = attrs.get("destination_station", getattr(self.instance, "destination_station", None))
        if source and destination and source.pk == destination.pk:
            raise serializers.ValidationError({"destination_code": "Choose a destination different from the origin."})
        date = attrs.get("journey_date", getattr(self.instance, "journey_date", None))
        if date and date < timezone.localdate():
            raise serializers.ValidationError({"journey_date": "Journey date must be today or later."})
        return attrs


class BookingPlanReminderCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookingReminder
        fields = ("remind_at",)

    def validate_remind_at(self, value):
        if value <= timezone.now():
            raise serializers.ValidationError("Choose a reminder time in the future.")
        return value
