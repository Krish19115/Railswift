from django.db import models


class Station(models.Model):
    code = models.CharField(max_length=8, unique=True)
    name = models.CharField(max_length=160, db_index=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("name",)

    def __str__(self):
        return f"{self.name} ({self.code})"
