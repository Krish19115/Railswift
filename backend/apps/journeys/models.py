from django.conf import settings
from django.db import models

from apps.stations.models import Station


class SavedJourney(models.Model):
    CLASS_CHOICES = [(code, code) for code in ("SL", "3A", "2A", "1A", "CC", "EC", "2S")]
    QUOTA_CHOICES = [(code, code) for code in ("GN", "TQ", "LD", "SS")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="saved_journeys")
    label = models.CharField(max_length=80, blank=True)
    source_station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="saved_journey_origins")
    destination_station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="saved_journey_destinations")
    journey_date = models.DateField(null=True, blank=True)
    preferred_class = models.CharField(max_length=2, choices=CLASS_CHOICES, default="SL")
    quota = models.CharField(max_length=2, choices=QUOTA_CHOICES, default="GN")
    is_favorite = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at",)
        constraints = [
            models.UniqueConstraint(
                fields=("user", "source_station", "destination_station", "journey_date"),
                name="unique_saved_journey_per_user_date",
            ),
        ]

    def __str__(self):
        return f"{self.source_station.code} to {self.destination_station.code}"
