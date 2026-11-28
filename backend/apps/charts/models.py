from django.db import models

from apps.stations.models import Station
from apps.trains.models import Train


class ChartSnapshot(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("first_prepared", "First chart prepared"), ("final", "Final chart prepared")]

    train = models.ForeignKey(Train, on_delete=models.PROTECT, related_name="chart_snapshots")
    journey_date = models.DateField()
    source_label = models.CharField(max_length=80)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES)
    captured_at = models.DateTimeField()
    class_code = models.CharField(max_length=2, blank=True)

    class Meta:
        ordering = ("-captured_at",)
        indexes = [models.Index(fields=("train", "journey_date", "captured_at"))]


class CoachVacancySnapshot(models.Model):
    chart_snapshot = models.ForeignKey(ChartSnapshot, on_delete=models.CASCADE, related_name="coaches")
    coach_number = models.CharField(max_length=20)
    class_code = models.CharField(max_length=2)
    segment_from = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="vacancy_segments_from")
    segment_to = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="vacancy_segments_to")
    vacant_count = models.PositiveSmallIntegerField()
    occupied_count = models.PositiveSmallIntegerField()

    class Meta:
        ordering = ("coach_number", "segment_from__code")
