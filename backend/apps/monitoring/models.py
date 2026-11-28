from django.conf import settings
from django.db import models


class PnrTracker(models.Model):
    STATUS_CHOICES = [
        ("unknown", "Unknown"),
        ("waitlisted", "Waitlisted"),
        ("confirmed", "Confirmed"),
        ("cancelled", "Cancelled"),
        ("chart_prepared", "Chart prepared"),
        ("error", "Provider error"),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="pnr_trackers")
    encrypted_pnr = models.TextField()
    pnr_fingerprint = models.CharField(max_length=64)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="unknown")
    last_checked_at = models.DateTimeField(null=True, blank=True)
    last_error = models.CharField(max_length=240, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ("-updated_at",)
        constraints = [models.UniqueConstraint(fields=("user", "pnr_fingerprint"), name="unique_user_pnr_fingerprint")]
        indexes = [models.Index(fields=("status", "updated_at"))]

    @property
    def masked_pnr(self):
        from .crypto import decrypt_pnr

        return f"••••••{decrypt_pnr(self.encrypted_pnr)[-4:]}"
