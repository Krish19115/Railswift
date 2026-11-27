from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [("stations", "0001_initial")]
    operations = [
        migrations.CreateModel(
            name="Train",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("number", models.CharField(max_length=10, unique=True)),
                ("name", models.CharField(db_index=True, max_length=160)),
                ("runs_daily", models.BooleanField(default=True)),
                ("is_demo", models.BooleanField(default=True)),
                ("is_active", models.BooleanField(default=True)),
            ],
            options={"ordering": ("number",)},
        ),
        migrations.CreateModel(
            name="TrainStop",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("stop_order", models.PositiveSmallIntegerField()),
                ("day_offset", models.PositiveSmallIntegerField(default=0)),
                ("arrival_time", models.TimeField(blank=True, null=True)),
                ("departure_time", models.TimeField(blank=True, null=True)),
                ("station", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="train_stops", to="stations.station")),
                ("train", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="stops", to="trains.train")),
            ],
            options={"ordering": ("stop_order",)},
        ),
        migrations.AddField(
            model_name="train",
            name="stations",
            field=models.ManyToManyField(related_name="trains", through="trains.TrainStop", to="stations.station"),
        ),
        migrations.AddConstraint(
            model_name="trainstop",
            constraint=models.UniqueConstraint(fields=("train", "stop_order"), name="unique_train_stop_order"),
        ),
        migrations.AddConstraint(
            model_name="trainstop",
            constraint=models.UniqueConstraint(fields=("train", "station"), name="unique_train_station"),
        ),
    ]
