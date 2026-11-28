from django.db.models import Count
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from apps.historical.models import WaitlistObservation
from .models import ConfirmationPrediction, ModelVersion
from .serializers import ModelVersionSerializer, PredictionRequestSerializer
from .service import ModelUnavailable, model_status, predict


class ModelStatusView(APIView):
    permission_classes = [permissions.AllowAny]

    def get(self, request):
        model = model_status()
        if not model:
            return Response({"status": "unavailable", "detail": "No trained model is active."})
        return Response({"status": "ready", "model": ModelVersionSerializer(model).data})


class ConfirmationPredictionView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        serializer = PredictionRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data
        try:
            result = predict(data)
        except ModelUnavailable as exc:
            return Response({"status": "unavailable", "detail": str(exc)}, status=status.HTTP_503_SERVICE_UNAVAILABLE)

        version = result["model_version"]
        record = ConfirmationPrediction.objects.create(
            user=request.user if request.user.is_authenticated else None,
            train=data["train"], source_station=data["source_station"], destination_station=data["destination_station"],
            journey_date=data["journey_date"], travel_class=data["travel_class"], quota=data["quota"],
            initial_waitlist=data["initial_waitlist"], current_waitlist=data["current_waitlist"], days_remaining=data["days_remaining"],
            confirmed_probability=result["probabilities"]["confirmed"], rac_probability=result["probabilities"]["rac"],
            waitlisted_probability=result["probabilities"]["waitlisted"], confidence_level=result["confidence"],
            comparable_records=result["comparable_journeys"], model_version=version,
        )
        return Response({
            "id": record.pk,
            "status": "success",
            "prediction": result["probabilities"],
            "confidence": result["confidence"],
            "comparable_journeys": result["comparable_journeys"],
            "model": {"version": version.version, "algorithm": version.algorithm, "trained_at": version.trained_at},
            "caveat": "Estimate from historical records only; ticket outcomes are not guaranteed.",
        })


class PredictionHistoryView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def list(self, request, *args, **kwargs):
        rows = ConfirmationPrediction.objects.filter(user=request.user).select_related("train", "model_version")[:50]
        return Response([{
            "id": row.pk, "train_number": row.train.number, "journey_date": row.journey_date,
            "confirmed": row.confirmed_probability, "rac": row.rac_probability, "waitlisted": row.waitlisted_probability,
            "confidence": row.confidence_level, "model_version": row.model_version.version, "predicted_at": row.predicted_at,
        } for row in rows])


class ModelMetricsView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        current = model_status()
        counts = dict(WaitlistObservation.objects.values_list("final_outcome").annotate(count=Count("id")))
        return Response({"active_model": ModelVersionSerializer(current).data if current else None, "outcome_records": counts})
