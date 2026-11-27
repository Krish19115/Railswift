from django.db import models

from apps.stations.models import Station


class Train(models.Model):
    number = models.CharField(max_length=10, unique=True)
    name = models.CharField(max_length=160, db_index=True)
    runs_daily = models.BooleanField(default=True)
    is_demo = models.BooleanField(default=True)
    is_active = models.BooleanField(default=True)
    stations = models.ManyToManyField(Station, through="TrainStop", related_name="trains")

    class Meta:
        ordering = ("number",)

    def __str__(self):
        return f"{self.number} {self.name}"


class TrainStop(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="stops")
    station = models.ForeignKey(Station, on_delete=models.PROTECT, related_name="train_stops")
    stop_order = models.PositiveSmallIntegerField()
    day_offset = models.PositiveSmallIntegerField(default=0)
    arrival_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)

    class Meta:
        ordering = ("stop_order",)
        constraints = [
            models.UniqueConstraint(fields=("train", "stop_order"), name="unique_train_stop_order"),
            models.UniqueConstraint(fields=("train", "station"), name="unique_train_station"),
        ]

    def __str__(self):
        return f"{self.train.number} · {self.station.code}"
