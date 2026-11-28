from django.conf import settings
from django.db import models


class NotificationLog(models.Model):
    CHANNEL_CHOICES = [("email", "Email"), ("push", "Push")]
    STATUS_CHOICES = [("queued", "Queued"), ("sent", "Sent"), ("failed", "Failed")]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="notification_logs")
    kind = models.CharField(max_length=40)
    channel = models.CharField(max_length=12, choices=CHANNEL_CHOICES, default="email")
    title = models.CharField(max_length=160)
    message = models.TextField()
    status = models.CharField(max_length=12, choices=STATUS_CHOICES, default="queued")
    created_at = models.DateTimeField(auto_now_add=True)
    sent_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ("-created_at",)
