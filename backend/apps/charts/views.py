from datetime import date

from django.db import transaction
from django.utils import timezone
from rest_framework import status
from rest_framework.exceptions import APIException, ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from integrations.base import ProviderUnavailable
from integrations.provider_factory import get_authorized_provider
from apps.stations.models import Station
from apps.trains.models import Train
from .models import ChartSnapshot, CoachVacancySnapshot
from .serializers import ChartSnapshotSerializer


class ChartSourceUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "Reservation chart data requires a configured authorized railway provider."
    default_code = "chart_source_unavailable"


class ChartQueryView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request):
        train_number = request.query_params.get("train_number", "").strip()
        journey_date = request.query_params.get("journey_date", "").strip()
        if not train_number or not journey_date:
            raise ValidationError({"detail": "train_number and journey_date are required."})
        try:
            date.fromisoformat(journey_date)
        except ValueError as exc:
            raise ValidationError({"journey_date": "Use YYYY-MM-DD."}) from exc
        train = Train.objects.filter(number=train_number, is_active=True).first()
        if train is None:
            raise ValidationError({"train_number": "Unknown train number."})
        try:
            provider = get_authorized_provider()
            payload = provider.get_chart(train_number, journey_date)
        except (ProviderUnavailable, ImportError, AttributeError):
            raise ChartSourceUnavailable()
        snapshot = self._save_snapshot(train, journey_date, provider, payload)
        return Response(ChartSnapshotSerializer(snapshot).data)

    @staticmethod
    def _save_snapshot(train, journey_date, provider, payload):
        if not isinstance(payload, dict) or payload.get("status") not in {"pending", "first_prepared", "final"}:
            raise ChartSourceUnavailable("The configured provider returned an invalid chart response.")
        entries = payload.get("coaches", [])
        if not isinstance(entries, list):
            raise ChartSourceUnavailable("The configured provider returned an invalid chart response.")
        try:
            with transaction.atomic():
                snapshot = ChartSnapshot.objects.create(
                    train=train,
                    journey_date=journey_date,
                    source_label=str(getattr(provider, "source_label", "authorized source"))[:80],
                    status=payload["status"],
                    captured_at=timezone.now(),
                    class_code=str(payload.get("class_code", ""))[:2],
                )
                vacancies = []
                stops = list(train.stops.order_by("stop_order").values_list("station__code", "stop_order"))
                stop_orders = dict(stops)
                for entry in entries:
                    source = Station.objects.get(code=str(entry["from_station"]).upper(), is_active=True)
                    destination = Station.objects.get(code=str(entry["to_station"]).upper(), is_active=True)
                    if source.code not in stop_orders or destination.code not in stop_orders or stop_orders[destination.code] <= stop_orders[source.code]:
                        raise ValueError("Chart segment is not in forward train order.")
                    vacant = int(entry["vacant_count"])
                    occupied = int(entry["occupied_count"])
                    if vacant < 0 or occupied < 0 or vacant > 32767 or occupied > 32767:
                        raise ValueError("Counts cannot be negative.")
                    vacancies.append(CoachVacancySnapshot(
                        chart_snapshot=snapshot,
                        coach_number=str(entry["coach_number"])[:20],
                        class_code=str(entry.get("class_code", ""))[:2],
                        segment_from=source,
                        segment_to=destination,
                        vacant_count=vacant,
                        occupied_count=occupied,
                    ))
                CoachVacancySnapshot.objects.bulk_create(vacancies)
        except (KeyError, TypeError, ValueError, Station.DoesNotExist) as exc:
            raise ChartSourceUnavailable("The configured provider returned an invalid chart response.") from exc
        return snapshot


class LatestChartView(APIView):
    permission_classes = (IsAuthenticated,)

    def get(self, request, snapshot_id):
        snapshot = ChartSnapshot.objects.filter(pk=snapshot_id).select_related("train").prefetch_related("coaches__segment_from", "coaches__segment_to").first()
        if snapshot is None:
            return Response({"detail": "Chart snapshot not found."}, status=404)
        return Response(ChartSnapshotSerializer(snapshot).data)
