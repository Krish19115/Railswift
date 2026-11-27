from rest_framework import serializers

from apps.stations.serializers import StationSerializer
from .models import Train, TrainStop


class TrainStopSerializer(serializers.ModelSerializer):
    station = StationSerializer(read_only=True)

    class Meta:
        model = TrainStop
        fields = ("station", "stop_order", "day_offset", "arrival_time", "departure_time")


class TrainSerializer(serializers.ModelSerializer):
    class Meta:
        model = Train
        fields = ("number", "name", "runs_daily", "is_demo")


class TrainDetailSerializer(TrainSerializer):
    stops = TrainStopSerializer(many=True, read_only=True)

    class Meta(TrainSerializer.Meta):
        fields = TrainSerializer.Meta.fields + ("stops",)
