from django.db import transaction
from django.db.models import Count, Min, Max
from rest_framework import permissions, status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from .importer import import_csv_file
from .models import WaitlistObservation


class WaitlistCoverageView(APIView):
    permission_classes = [permissions.IsAdminUser]

    def get(self, request):
        summary = WaitlistObservation.objects.aggregate(
            records=Count("id"), journeys=Count("journey_key", distinct=True),
            first_capture=Min("captured_at"), latest_capture=Max("captured_at"),
        )
        outcomes = dict(WaitlistObservation.objects.values_list("final_outcome").annotate(count=Count("id")))
        return Response({**summary, "outcomes": outcomes, "training_ready": summary["journeys"] >= 50 and all(outcomes.get(code, 0) > 0 for code in ("CNF", "RAC", "WL"))})


class WaitlistImportView(APIView):
    permission_classes = [permissions.IsAdminUser]
    parser_classes = [MultiPartParser]

    def post(self, request):
        uploaded = request.FILES.get("file")
        if not uploaded:
            return Response({"detail": "Attach a CSV using the file field."}, status=status.HTTP_400_BAD_REQUEST)
        if uploaded.size > 5 * 1024 * 1024:
            return Response({"detail": "CSV must be 5 MB or smaller."}, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)
        try:
            with transaction.atomic():
                created = import_csv_file(uploaded)
        except ValueError as exc:
            return Response({"detail": str(exc)}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"created": created, "message": "De-identified historical observations imported."}, status=status.HTTP_201_CREATED)
