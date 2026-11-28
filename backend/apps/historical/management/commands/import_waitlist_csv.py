from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from apps.historical.importer import import_csv_file


class Command(BaseCommand):
    help = "Import de-identified waitlist snapshots from a UTF-8 CSV file."

    def add_arguments(self, parser):
        parser.add_argument("path")

    def handle(self, *args, **options):
        try:
            with open(options["path"], "rb") as file_obj, transaction.atomic():
                created = import_csv_file(file_obj)
        except (OSError, ValueError) as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(f"Imported {created} de-identified observations."))
