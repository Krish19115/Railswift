from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True
    dependencies = [("stations", "0001_initial"), ("trains", "0001_initial")]
    operations = [
        migrations.CreateModel(name="ChartSnapshot", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("journey_date", models.DateField()), ("source_label", models.CharField(max_length=80)),
            ("status", models.CharField(choices=[("pending", "Pending"), ("first_prepared", "First chart prepared"), ("final", "Final chart prepared")], max_length=20)),
            ("captured_at", models.DateTimeField()), ("class_code", models.CharField(blank=True, max_length=2)),
            ("train", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="chart_snapshots", to="trains.train")),
        ], options={"ordering": ("-captured_at",)}),
        migrations.AddIndex(model_name="chartsnapshot", index=models.Index(fields=["train", "journey_date", "captured_at"], name="charts_charts_train_n_0f520d_idx")),
        migrations.CreateModel(name="CoachVacancySnapshot", fields=[
            ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
            ("coach_number", models.CharField(max_length=20)), ("class_code", models.CharField(max_length=2)),
            ("vacant_count", models.PositiveSmallIntegerField()), ("occupied_count", models.PositiveSmallIntegerField()),
            ("chart_snapshot", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="coaches", to="charts.chartsnapshot")),
            ("segment_from", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="vacancy_segments_from", to="stations.station")),
            ("segment_to", models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name="vacancy_segments_to", to="stations.station")),
        ], options={"ordering": ("coach_number", "segment_from__code")})
    ]
