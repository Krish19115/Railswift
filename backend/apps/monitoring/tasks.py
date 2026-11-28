from datetime import timedelta

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from integrations.base import ProviderUnavailable
from integrations.provider_factory import get_authorized_provider
from apps.notifications.models import NotificationLog
from .crypto import decrypt_pnr
from .models import PnrTracker


@shared_task
def check_due_pnr_trackers():
    try:
        provider = get_authorized_provider()
    except (ProviderUnavailable, ImportError, AttributeError):
        return {"checked": 0, "provider_available": False}

    cutoff = timezone.now() - timedelta(minutes=15)
    checked = 0
    trackers = PnrTracker.objects.filter(updated_at__lt=cutoff).exclude(status__in=("confirmed", "cancelled", "chart_prepared"))
    for tracker in trackers.select_related("user").iterator(chunk_size=100):
        old_status = tracker.status
        try:
            result = provider.get_pnr_status(decrypt_pnr(tracker.encrypted_pnr))
            if not isinstance(result, dict):
                raise ValueError("Invalid provider response.")
            raw_status = str(result.get("status", "unknown")).lower()
            allowed = {item[0] for item in PnrTracker.STATUS_CHOICES}
            tracker.status = raw_status if raw_status in allowed else "unknown"
            tracker.last_error = ""
        except Exception:  # noqa: BLE001 - keep PNRs and provider exception text out of worker logs
            tracker.status = "error"
            tracker.last_error = "The authorized status check could not be completed."
        tracker.last_checked_at = timezone.now()
        tracker.save(update_fields=("status", "last_error", "last_checked_at", "updated_at"))
        if tracker.status != old_status and tracker.status != "error":
            notification = NotificationLog.objects.create(
                user=tracker.user,
                kind="pnr_status",
                title="Your railway booking status changed",
                message=f"The latest authorized update is: {tracker.get_status_display()}.",
                channel="email",
                status="queued",
            )
            if tracker.user.email:
                try:
                    send_mail(notification.title, notification.message, settings.DEFAULT_FROM_EMAIL, [tracker.user.email])
                    notification.status = "sent"
                    notification.sent_at = timezone.now()
                except Exception:  # noqa: BLE001 - do not put PNR or provider data into email errors
                    notification.status = "failed"
                notification.save(update_fields=("status", "sent_at"))
            else:
                notification.status = "failed"
                notification.save(update_fields=("status",))
        checked += 1
    return {"checked": checked, "provider_available": True}
