from rest_framework import serializers
from django.utils import timezone

from apps.stations.models import Station
from apps.stations.serializers import StationSerializer
from .models import SavedJourney


class SavedJourneySerializer(serializers.ModelSerializer):
    source_station = StationSerializer(read_only=True)
    destination_station = StationSerializer(read_only=True)
    source_code = serializers.SlugRelatedField(
        source="source_station", slug_field="code", queryset=Station.objects.filter(is_active=True), write_only=True
    )
    destination_code = serializers.SlugRelatedField(
        source="destination_station", slug_field="code", queryset=Station.objects.filter(is_active=True), write_only=True
    )

    class Meta:
        model = SavedJourney
        fields = (
            "id", "label", "source_station", "destination_station", "source_code", "destination_code",
            "journey_date", "preferred_class", "quota", "is_favorite", "created_at",
        )
        read_only_fields = ("id", "created_at")

    def validate(self, attrs):
        source = attrs.get("source_station", getattr(self.instance, "source_station", None))
        destination = attrs.get("destination_station", getattr(self.instance, "destination_station", None))
        journey_date = attrs.get("journey_date", getattr(self.instance, "journey_date", None))
        if source and destination and source.pk == destination.pk:
            raise serializers.ValidationError({"destination_code": "Choose a destination different from the origin."})
        request = self.context.get("request")
        if request and request.user.is_authenticated and source and destination:
            duplicates = SavedJourney.objects.filter(
                user=request.user,
                source_station=source,
                destination_station=destination,
                journey_date=journey_date,
            )
            if self.instance:
                duplicates = duplicates.exclude(pk=self.instance.pk)
            if duplicates.exists():
                raise serializers.ValidationError({"journey_date": "This journey is already saved."})
        return attrs

    def validate_journey_date(self, value):
        if value is not None and value < timezone.localdate():
            raise serializers.ValidationError("Journey date must be today or later.")
        return value
