from django.conf import settings
from django.db import models

from apps.stations.models import Station
from apps.trains.models import Train


class ModelVersion(models.Model):
    name = models.CharField(max_length=80)
    version = models.CharField(max_length=40, unique=True)
    algorithm = models.CharField(max_length=60)
    feature_version = models.CharField(max_length=40)
    artifact_path = models.CharField(max_length=500)
    training_records = models.PositiveIntegerField()
    journey_groups = models.PositiveIntegerField()
    brier_score = models.FloatField()
    log_loss = models.FloatField()
    accuracy = models.FloatField()
    trained_at = models.DateTimeField(auto_now_add=True)
    active = models.BooleanField(default=False, db_index=True)

    class Meta:
        ordering = ("-trained_at",)


class ConfirmationPrediction(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, null=True, blank=True, on_delete=models.SET_NULL, related_name="confirmation_predictions")
    train = models.ForeignKey(Train, on_delete=models.PROTECT, related_name="predictions")
    source_station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="predictions_from")
    destination_station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="predictions_to")
    journey_date = models.DateField()
    travel_class = models.CharField(max_length=2)
    quota = models.CharField(max_length=3)
    initial_waitlist = models.PositiveIntegerField()
    current_waitlist = models.PositiveIntegerField()
    days_remaining = models.PositiveSmallIntegerField()
    confirmed_probability = models.FloatField()
    rac_probability = models.FloatField()
    waitlisted_probability = models.FloatField()
    confidence_level = models.CharField(max_length=16)
    comparable_records = models.PositiveIntegerField()
    model_version = models.ForeignKey(ModelVersion, on_delete=models.PROTECT, related_name="predictions")
    predicted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-predicted_at",)
