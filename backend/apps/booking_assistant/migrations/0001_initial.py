from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ("stations", "0001_initial")]
    operations = [
        migrations.CreateModel(name="BookingPlan", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("label", models.CharField(blank=True, max_length=80)), ("journey_date", models.DateField()),
            ("preferred_class", models.CharField(choices=[("SL", "SL"), ("3A", "3A"), ("2A", "2A"), ("1A", "1A"), ("CC", "CC"), ("EC", "EC"), ("2S", "2S")], default="SL", max_length=2)),
            ("quota", models.CharField(choices=[("GN", "GN"), ("TQ", "TQ"), ("LD", "LD"), ("SS", "SS")], default="GN", max_length=2)),
            ("booking_opens_at", models.DateTimeField(blank=True, null=True)),
            ("status", models.CharField(choices=[("planned", "Planned"), ("booked", "Booked"), ("cancelled", "Cancelled")], default="planned", max_length=12)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("destination_station", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="booking_plan_destinations", to="stations.station")),
            ("source_station", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="booking_plan_origins", to="stations.station")),
            ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="booking_plans", to=settings.AUTH_USER_MODEL)),
        ], options={"ordering": ("journey_date", "created_at")}),
        migrations.CreateModel(name="BookingReminder", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("remind_at", models.DateTimeField(db_index=True)),
            ("status", models.CharField(choices=[("pending", "Pending"), ("sent", "Sent"), ("failed", "Failed"), ("cancelled", "Cancelled")], default="pending", max_length=12)),
            ("sent_at", models.DateTimeField(blank=True, null=True)), ("last_error", models.CharField(blank=True, max_length=240)),
            ("created_at", models.DateTimeField(auto_now_add=True)),
            ("booking_plan", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="reminders", to="booking_assistant.bookingplan")),
            ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="booking_reminders", to=settings.AUTH_USER_MODEL)),
        ], options={"ordering": ("remind_at",)}),
    ]
