import uuid
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [("stations", "0001_initial"), ("trains", "0001_initial")]
    operations = [
        migrations.CreateModel(name="WaitlistObservation", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("journey_key", models.UUIDField(db_index=True, default=uuid.uuid4)), ("journey_date", models.DateField(db_index=True)),
            ("travel_class", models.CharField(choices=[("SL", "SL"), ("3A", "3A"), ("2A", "2A"), ("1A", "1A"), ("CC", "CC"), ("EC", "EC"), ("2S", "2S")], max_length=2)),
            ("quota", models.CharField(choices=[("GN", "GN"), ("TQ", "TQ"), ("RL", "RL"), ("PQ", "PQ"), ("LD", "LD"), ("SS", "SS")], max_length=2)),
            ("initial_waitlist", models.PositiveIntegerField()), ("current_waitlist", models.PositiveIntegerField()),
            ("days_remaining", models.PositiveSmallIntegerField()),
            ("final_outcome", models.CharField(choices=[("CNF", "Confirmed"), ("RAC", "RAC"), ("WL", "Waitlisted")], max_length=3)),
            ("captured_at", models.DateTimeField(db_index=True)), ("source_label", models.CharField(blank=True, max_length=80)),
            ("destination_station", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="waitlist_destinations", to="stations.station")),
            ("source_station", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="waitlist_origins", to="stations.station")),
            ("train", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="waitlist_observations", to="trains.train")),
        ], options={"ordering": ("-captured_at",)}),
        migrations.AddIndex(model_name="waitlistobservation", index=models.Index(fields=["train", "source_station", "destination_station", "travel_class", "quota"], name="historical_train__5f8704_idx")),
        migrations.AddIndex(model_name="waitlistobservation", index=models.Index(fields=["journey_key", "captured_at"], name="historical_journey_52d0aa_idx")),
    ]
