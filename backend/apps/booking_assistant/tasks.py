from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone

from apps.notifications.models import NotificationLog
from .models import BookingReminder


@shared_task
def dispatch_due_reminders():
    now = timezone.now()
    due = BookingReminder.objects.select_related("user", "booking_plan__source_station", "booking_plan__destination_station").filter(
        status="pending", remind_at__lte=now, booking_plan__status="planned"
    )
    delivered = 0
    for reminder in due.iterator():
        plan = reminder.booking_plan
        if not reminder.user.email:
            reminder.status = "failed"
            reminder.last_error = "No email address is set on this account."
            reminder.save(update_fields=("status", "last_error"))
            continue
        title = "Your RailSwift journey reminder"
        message = (
            f"Your planned journey from {plan.source_station.name} to {plan.destination_station.name} "
            f"is scheduled for {plan.journey_date:%d %b %Y}. Complete booking on the official railway site."
        )
        try:
            send_mail(title, message, settings.DEFAULT_FROM_EMAIL, [reminder.user.email], fail_silently=False)
        except Exception as exc:  # noqa: BLE001 - keep one delivery failure from stopping the queue
            reminder.status = "failed"
            reminder.last_error = str(exc)[:240]
            reminder.save(update_fields=("status", "last_error"))
            NotificationLog.objects.create(user=reminder.user, kind="booking_reminder", title=title, message=message, status="failed")
            continue
        reminder.status = "sent"
        reminder.sent_at = now
        reminder.save(update_fields=("status", "sent_at"))
        NotificationLog.objects.create(user=reminder.user, kind="booking_reminder", title=title, message=message, status="sent", sent_at=now)
        delivered += 1
    return {"sent": delivered}
