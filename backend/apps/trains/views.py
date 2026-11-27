from datetime import datetime, timedelta

from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework.views import APIView
from django.utils import timezone

from apps.stations.models import Station
from .models import Train, TrainStop
from .serializers import TrainDetailSerializer, TrainSerializer, TrainStopSerializer


class TrainListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = TrainSerializer
    queryset = Train.objects.filter(is_active=True)
    pagination_class = None

    def get_queryset(self):
        queryset = super().get_queryset()
        query = self.request.query_params.get("search", "").strip()
        if query:
            queryset = queryset.filter(Q(number__istartswith=query) | Q(name__icontains=query))
        return queryset[:50]


class TrainDetailView(generics.RetrieveAPIView):
    permission_classes = [AllowAny]
    serializer_class = TrainDetailSerializer
    queryset = Train.objects.filter(is_active=True).prefetch_related("stops__station")
    lookup_field = "number"


class TrainScheduleView(APIView):
    permission_classes = [AllowAny]

    def get(self, request, number):
        train = get_object_or_404(Train.objects.filter(is_active=True).prefetch_related("stops__station"), number=number)
        return Response({"train": TrainSerializer(train).data, "stops": TrainStopSerializer(train.stops.all(), many=True).data})


class TrainsBetweenView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        source_code = request.query_params.get("from", "").strip().upper()
        destination_code = request.query_params.get("to", "").strip().upper()
        date_text = request.query_params.get("date", "").strip()
        if not source_code or not destination_code or not date_text:
            raise ValidationError({"detail": "from, to, and date are required."})
        if source_code == destination_code:
            raise ValidationError({"to": "Choose a destination different from the origin."})
        try:
            journey_date = datetime.strptime(date_text, "%Y-%m-%d").date()
        except ValueError as exc:
            raise ValidationError({"date": "Use YYYY-MM-DD format."}) from exc
        if journey_date.isoformat() != date_text:
            raise ValidationError({"date": "Use YYYY-MM-DD format."})
        if journey_date < timezone.localdate():
            raise ValidationError({"date": "Journey date must be today or later."})

        stations = {station.code: station for station in Station.objects.filter(code__in=(source_code, destination_code), is_active=True)}
        if source_code not in stations:
            raise ValidationError({"from": "Unknown station code."})
        if destination_code not in stations:
            raise ValidationError({"to": "Unknown station code."})

        source_stops = TrainStop.objects.filter(
            station=stations[source_code], train__is_active=True, train__runs_daily=True
        ).select_related("train", "station")
        matches = []
        for source_stop in source_stops:
            destination_stop = TrainStop.objects.filter(
                train=source_stop.train,
                station=stations[destination_code],
                stop_order__gt=source_stop.stop_order,
            ).select_related("station").first()
            if destination_stop is None:
                continue

            departure_time = source_stop.departure_time or source_stop.arrival_time
            arrival_time = destination_stop.arrival_time or destination_stop.departure_time
            departure_at = None
            arrival_at = None
            duration_minutes = None
            if departure_time and arrival_time:
                departure_at = datetime.combine(
                    journey_date + timedelta(days=source_stop.day_offset), departure_time
                )
                arrival_at = datetime.combine(
                    journey_date + timedelta(days=destination_stop.day_offset), arrival_time
                )
                if arrival_at < departure_at:
                    arrival_at += timedelta(days=1)
                duration_minutes = int((arrival_at - departure_at).total_seconds() // 60)

            matches.append({
                "train": {"number": source_stop.train.number, "name": source_stop.train.name, "is_demo": source_stop.train.is_demo},
                "from": {"station": source_stop.station.code, "name": source_stop.station.name, "departure_time": departure_time.strftime("%H:%M") if departure_time else None},
                "to": {"station": destination_stop.station.code, "name": destination_stop.station.name, "arrival_time": arrival_time.strftime("%H:%M") if arrival_time else None},
                "departure_at": departure_at.isoformat() if departure_at else None,
                "arrival_at": arrival_at.isoformat() if arrival_at else None,
                "duration_minutes": duration_minutes,
                "journey_date": journey_date.isoformat(),
            })

        matches.sort(key=lambda item: item["departure_at"] or "")
        return Response({
            "results": matches,
            "count": len(matches),
            "source": "demo" if any(item["train"]["is_demo"] for item in matches) else "catalog",
            "notice": "Sample timetable data for development; not live railway information.",
        })
