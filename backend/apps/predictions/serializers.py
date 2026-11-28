from rest_framework import serializers
from django.utils import timezone

from apps.stations.models import Station
from apps.trains.models import Train, TrainStop


class PredictionRequestSerializer(serializers.Serializer):
    train_number = serializers.CharField(max_length=10)
    source = serializers.CharField(max_length=8)
    destination = serializers.CharField(max_length=8)
    journey_date = serializers.DateField()
    travel_class = serializers.ChoiceField(choices=("SL", "3A", "2A", "1A", "CC", "EC", "2S"))
    quota = serializers.ChoiceField(choices=("GN", "TQ", "RL", "PQ", "LD", "SS"))
    initial_waitlist = serializers.IntegerField(min_value=0, max_value=10000)
    current_waitlist = serializers.IntegerField(min_value=0, max_value=10000)
    days_remaining = serializers.IntegerField(min_value=0, max_value=365)

    def validate(self, attrs):
        if attrs["journey_date"] < timezone.localdate():
            raise serializers.ValidationError({"journey_date": "Journey date must be today or later."})
        train = Train.objects.filter(number=attrs["train_number"], is_active=True).first()
        if not train:
            raise serializers.ValidationError({"train_number": "Unknown train number."})
        source = Station.objects.filter(code__iexact=attrs["source"], is_active=True).first()
        destination = Station.objects.filter(code__iexact=attrs["destination"], is_active=True).first()
        if not source:
            raise serializers.ValidationError({"source": "Unknown station code."})
        if not destination:
            raise serializers.ValidationError({"destination": "Unknown station code."})
        if source.pk == destination.pk:
            raise serializers.ValidationError({"destination": "Choose a different destination station."})
        source_stop = TrainStop.objects.filter(train=train, station=source).first()
        destination_stop = TrainStop.objects.filter(train=train, station=destination).first()
        if not source_stop or not destination_stop or destination_stop.stop_order <= source_stop.stop_order:
            raise serializers.ValidationError({"destination": "This train does not serve the requested segment."})
        attrs["train"] = train
        attrs["source_station"] = source
        attrs["destination_station"] = destination
        return attrs


class ModelVersionSerializer(serializers.ModelSerializer):
    class Meta:
        from .models import ModelVersion

        model = ModelVersion
        fields = ("version", "algorithm", "feature_version", "training_records", "journey_groups", "brier_score", "log_loss", "accuracy", "trained_at")

