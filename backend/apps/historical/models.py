import uuid

from django.db import models

from apps.stations.models import Station
from apps.trains.models import Train


class WaitlistObservation(models.Model):
    OUTCOME_CHOICES = [("CNF", "Confirmed"), ("RAC", "RAC"), ("WL", "Waitlisted")]
    CLASS_CHOICES = [(code, code) for code in ("SL", "3A", "2A", "1A", "CC", "EC", "2S")]
    QUOTA_CHOICES = [(code, code) for code in ("GN", "TQ", "RL", "PQ", "LD", "SS")]

    # Random opaque journey grouping key. Do not put a PNR or passenger identifier here.
    journey_key = models.UUIDField(default=uuid.uuid4, db_index=True)
    train = models.ForeignKey(Train, on_delete=models.PROTECT, related_name="waitlist_observations")
    source_station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="waitlist_origins")
    destination_station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="waitlist_destinations")
    journey_date = models.DateField(db_index=True)
    travel_class = models.CharField(max_length=2, choices=CLASS_CHOICES)
    quota = models.CharField(max_length=2, choices=QUOTA_CHOICES)
    initial_waitlist = models.PositiveIntegerField()
    current_waitlist = models.PositiveIntegerField()
    days_remaining = models.PositiveSmallIntegerField()
    final_outcome = models.CharField(max_length=3, choices=OUTCOME_CHOICES)
    captured_at = models.DateTimeField(db_index=True)
    source_label = models.CharField(max_length=80, blank=True)

    class Meta:
        ordering = ("-captured_at",)
        indexes = [
            models.Index(fields=("train", "source_station", "destination_station", "travel_class", "quota")),
            models.Index(fields=("journey_key", "captured_at")),
        ]

    def __str__(self):
        return f"{self.train.number} {self.journey_date} · {self.final_outcome}"
