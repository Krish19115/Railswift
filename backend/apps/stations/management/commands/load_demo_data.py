from datetime import time

from django.core.management.base import BaseCommand
from django.db import transaction

from apps.stations.models import Station
from apps.trains.models import Train, TrainStop


STATIONS = [
    ("NDLS", "New Delhi", "Delhi", "Delhi"),
    ("JP", "Jaipur Junction", "Jaipur", "Rajasthan"),
    ("ADI", "Ahmedabad Junction", "Ahmedabad", "Gujarat"),
    ("BRC", "Vadodara Junction", "Vadodara", "Gujarat"),
    ("ST", "Surat", "Surat", "Gujarat"),
    ("MMCT", "Mumbai Central", "Mumbai", "Maharashtra"),
]

# RS-prefixed services and all timings below are fictional demonstration data.
TRAINS = [
    ("RS101", "Demo Western Connector", [("NDLS", "06:00", "06:20", 0), ("JP", "10:10", "10:20", 0), ("ADI", "16:30", "16:40", 0), ("BRC", "18:20", "18:25", 0), ("MMCT", "23:30", "23:45", 0)]),
    ("RS102", "Demo Coastline Express", [("ADI", "07:15", "07:30", 0), ("BRC", "09:05", "09:10", 0), ("ST", "11:20", "11:25", 0), ("MMCT", "14:40", "14:55", 0)]),
    ("RS103", "Demo Desert Link", [("NDLS", "20:00", "20:15", 0), ("JP", "00:10", "00:20", 1), ("ADI", "06:45", "06:55", 1), ("BRC", "08:35", "08:40", 1), ("ST", "10:50", "10:55", 1), ("MMCT", "14:05", "14:20", 1)]),
    ("RS104", "Demo Gujarat Local", [("ADI", "13:00", "13:10", 0), ("BRC", "14:50", "14:55", 0), ("ST", "16:35", "16:40", 0), ("MMCT", "19:50", "20:05", 0)]),
]


def parse_time(value):
    hour, minute = (int(part) for part in value.split(":"))
    return time(hour, minute)


class Command(BaseCommand):
    help = "Load clearly labeled fictional RailSwift stations and timetable records for development."

    @transaction.atomic
    def handle(self, *args, **options):
        stations = {}
        for code, name, city, state in STATIONS:
            stations[code], _ = Station.objects.update_or_create(
                code=code,
                defaults={"name": name, "city": city, "state": state, "is_active": True},
            )

        for number, name, stop_data in TRAINS:
            train, _ = Train.objects.update_or_create(
                number=number,
                defaults={"name": name, "runs_daily": True, "is_demo": True, "is_active": True},
            )
            for order, (code, arrival, departure, day_offset) in enumerate(stop_data, start=1):
                TrainStop.objects.update_or_create(
                    train=train,
                    stop_order=order,
                    defaults={
                        "station": stations[code],
                        "arrival_time": parse_time(arrival),
                        "departure_time": parse_time(departure),
                        "day_offset": day_offset,
                    },
                )

        self.stdout.write(self.style.SUCCESS("Loaded fictional RailSwift demo timetable data (RS101–RS104)."))
