from rest_framework import serializers

from .models import WaitlistObservation


class WaitlistObservationSerializer(serializers.ModelSerializer):
    class Meta:
        model = WaitlistObservation
        fields = (
            "journey_key", "train", "source_station", "destination_station", "journey_date", "travel_class",
            "quota", "initial_waitlist", "current_waitlist", "days_remaining", "final_outcome", "captured_at", "source_label",
        )
        read_only_fields = fields
