from django.core.management.base import BaseCommand, CommandError

from apps.predictions.training import train_confirmation_model


class Command(BaseCommand):
    help = "Train, evaluate, and activate a versioned waitlist outcome model from historical records."

    def handle(self, *args, **options):
        try:
            version, metrics, journey_groups = train_confirmation_model()
        except ValueError as exc:
            raise CommandError(str(exc)) from exc
        self.stdout.write(self.style.SUCCESS(
            f"Activated {version.version} ({version.algorithm}); journeys={journey_groups}, "
            f"log_loss={metrics['log_loss']:.4f}, brier={metrics['brier_score']:.4f}, accuracy={metrics['accuracy']:.4f}."
        ))
