from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [migrations.swappable_dependency(settings.AUTH_USER_MODEL), ("stations", "0001_initial"), ("trains", "0001_initial")]
    operations = [
        migrations.CreateModel(name="ModelVersion", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("name", models.CharField(max_length=80)), ("version", models.CharField(max_length=40, unique=True)),
            ("algorithm", models.CharField(max_length=60)), ("feature_version", models.CharField(max_length=40)),
            ("artifact_path", models.CharField(max_length=500)), ("training_records", models.PositiveIntegerField()),
            ("journey_groups", models.PositiveIntegerField()), ("brier_score", models.FloatField()),
            ("log_loss", models.FloatField()), ("accuracy", models.FloatField()),
            ("trained_at", models.DateTimeField(auto_now_add=True)), ("active", models.BooleanField(db_index=True, default=False)),
        ], options={"ordering": ("-trained_at",)}),
        migrations.CreateModel(name="ConfirmationPrediction", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("journey_date", models.DateField()), ("travel_class", models.CharField(max_length=2)), ("quota", models.CharField(max_length=3)),
            ("initial_waitlist", models.PositiveIntegerField()), ("current_waitlist", models.PositiveIntegerField()), ("days_remaining", models.PositiveSmallIntegerField()),
            ("confirmed_probability", models.FloatField()), ("rac_probability", models.FloatField()), ("waitlisted_probability", models.FloatField()),
            ("confidence_level", models.CharField(max_length=16)), ("comparable_records", models.PositiveIntegerField()), ("predicted_at", models.DateTimeField(auto_now_add=True)),
            ("destination_station", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="predictions_to", to="stations.station")),
            ("model_version", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="predictions", to="predictions.modelversion")),
            ("source_station", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="predictions_from", to="stations.station")),
            ("train", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="predictions", to="trains.train")),
            ("user", models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="confirmation_predictions", to=settings.AUTH_USER_MODEL)),
        ], options={"ordering": ("-predicted_at",)})
    ]
