import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):
    initial = True
    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("stations", "0001_initial"),
    ]
    operations = [
        migrations.CreateModel(
            name="SavedJourney",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("label", models.CharField(blank=True, max_length=80)),
                ("journey_date", models.DateField(blank=True, null=True)),
                ("preferred_class", models.CharField(choices=[("SL", "SL"), ("3A", "3A"), ("2A", "2A"), ("1A", "1A"), ("CC", "CC"), ("EC", "EC"), ("2S", "2S")], default="SL", max_length=2)),
                ("quota", models.CharField(choices=[("GN", "GN"), ("TQ", "TQ"), ("LD", "LD"), ("SS", "SS")], default="GN", max_length=2)),
                ("is_favorite", models.BooleanField(default=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("destination_station", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="saved_journey_destinations", to="stations.station")),
                ("source_station", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="saved_journey_origins", to="stations.station")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="saved_journeys", to=settings.AUTH_USER_MODEL)),
            ],
            options={"ordering": ("-created_at",)},
        ),
        migrations.AddConstraint(
            model_name="savedjourney",
            constraint=models.UniqueConstraint(fields=("user", "source_station", "destination_station", "journey_date"), name="unique_saved_journey_per_user_date"),
        ),
    ]
