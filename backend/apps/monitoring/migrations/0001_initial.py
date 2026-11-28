from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [
        migrations.CreateModel(name="PnrTracker", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("encrypted_pnr", models.TextField()), ("pnr_fingerprint", models.CharField(max_length=64)),
            ("status", models.CharField(choices=[("unknown", "Unknown"), ("waitlisted", "Waitlisted"), ("confirmed", "Confirmed"), ("cancelled", "Cancelled"), ("chart_prepared", "Chart prepared"), ("error", "Provider error")], default="unknown", max_length=20)),
            ("last_checked_at", models.DateTimeField(blank=True, null=True)), ("last_error", models.CharField(blank=True, max_length=240)),
            ("created_at", models.DateTimeField(auto_now_add=True)), ("updated_at", models.DateTimeField(auto_now=True)),
            ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="pnr_trackers", to=settings.AUTH_USER_MODEL)),
        ]),
        migrations.AddConstraint(model_name="pnrtracker", constraint=models.UniqueConstraint(fields=("user", "pnr_fingerprint"), name="unique_user_pnr_fingerprint")),
        migrations.AddIndex(model_name="pnrtracker", index=models.Index(fields=["status", "updated_at"], name="monitoring_status_996b5e_idx")),
    ]
