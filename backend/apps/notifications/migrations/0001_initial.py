from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL)]
    operations = [migrations.CreateModel(name="NotificationLog", fields=[
        ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
        ("kind", models.CharField(max_length=40)), ("channel", models.CharField(choices=[("email", "Email"), ("push", "Push")], default="email", max_length=12)),
        ("title", models.CharField(max_length=160)), ("message", models.TextField()),
        ("status", models.CharField(choices=[("queued", "Queued"), ("sent", "Sent"), ("failed", "Failed")], default="queued", max_length=12)),
        ("created_at", models.DateTimeField(auto_now_add=True)), ("sent_at", models.DateTimeField(blank=True, null=True)),
        ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="notification_logs", to=settings.AUTH_USER_MODEL)),
    ], options={"ordering": ("-created_at",)})]
