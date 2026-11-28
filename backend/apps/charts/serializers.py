from rest_framework import serializers

from .models import ChartSnapshot, CoachVacancySnapshot


class CoachVacancySerializer(serializers.ModelSerializer):
    from_station = serializers.CharField(source="segment_from.code", read_only=True)
    to_station = serializers.CharField(source="segment_to.code", read_only=True)

    class Meta:
        model = CoachVacancySnapshot
        fields = ("coach_number", "class_code", "from_station", "to_station", "vacant_count", "occupied_count")


class ChartSnapshotSerializer(serializers.ModelSerializer):
    train_number = serializers.CharField(source="train.number", read_only=True)
    coaches = CoachVacancySerializer(many=True, read_only=True)

    class Meta:
        model = ChartSnapshot
        fields = ("id", "train_number", "journey_date", "source_label", "status", "captured_at", "class_code", "coaches")
