from django.conf import settings
from django.db import models

from apps.stations.models import Station


class BookingPlan(models.Model):
    STATUS_CHOICES = [("planned", "Planned"), ("booked", "Booked"), ("cancelled", "Cancelled")]
    CLASS_CHOICES = [(code, code) for code in ("SL", "3A", "2A", "1A", "CC", "EC", "2S")]
    QUOTA_CHOICES = [(code, code) for code in ("GN", "TQ", "LD", "SS")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="booking_plans")
    label = models.CharField(max_length=80, blank=True)
    source_station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="booking_plan_origins")
    destination_station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="booking_plan_destinations")
    journey_date = models.DateField()
    preferred_class = models.CharField(max_length=2, choices=CLASS_CHOICES, default="SL")
    quota = models.CharField(max_length=2, choices=QUOTA_CHOICES, default="GN")
    booking_opens_at = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="planned")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("journey_date", "created_at")


class BookingReminder(models.Model):
    STATUS_CHOICES = [("pending", "Pending"), ("sent", "Sent"), ("failed", "Failed"), ("cancelled", "Cancelled")]

    booking_plan = models.ForeignKey(BookingPlan, on_delete=models.CASCADE, related_name="reminders")
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="booking_reminders")
    remind_at = models.DateTimeField(db_index=True)
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="pending")
    sent_at = models.DateTimeField(null=True, blank=True)
    last_error = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("remind_at",)
