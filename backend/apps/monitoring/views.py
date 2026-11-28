from django.db import IntegrityError, transaction
from django.utils import timezone
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import APIException
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from integrations.provider_factory import get_authorized_provider
from integrations.base import ProviderUnavailable
from .crypto import PnrEncryptionUnavailable, decrypt_pnr
from .models import PnrTracker
from .serializers import PnrTrackerSerializer


class PnrTrackingUnavailable(APIException):
    status_code = status.HTTP_503_SERVICE_UNAVAILABLE
    default_detail = "PNR tracking requires a configured authorized provider and encryption key."
    default_code = "pnr_tracking_unavailable"


class PnrTrackerViewSet(viewsets.ModelViewSet):
    serializer_class = PnrTrackerSerializer
    permission_classes = (IsAuthenticated,)
    http_method_names = ("get", "post", "delete", "head", "options")

    def get_queryset(self):
        return PnrTracker.objects.filter(user=self.request.user)

    def create(self, request, *args, **kwargs):
        try:
            get_authorized_provider()
        except (ProviderUnavailable, ImportError, AttributeError):
            raise PnrTrackingUnavailable()
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            with transaction.atomic():
                tracker = serializer.save(user=request.user)
        except IntegrityError:
            return Response({"detail": "This PNR is already being tracked."}, status=409)
        return Response(self.get_serializer(tracker).data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=("post",), url_path="check")
    def check_now(self, request, pk=None):
        tracker = self.get_object()
        try:
            provider = get_authorized_provider()
            pnr = decrypt_pnr(tracker.encrypted_pnr)
            result = provider.get_pnr_status(pnr)
        except (ProviderUnavailable, PnrEncryptionUnavailable, ImportError, AttributeError):
            raise PnrTrackingUnavailable()
        except Exception as exc:  # noqa: BLE001 - hide provider errors and never echo a PNR through them
            raise PnrTrackingUnavailable("The authorized provider could not complete the status check.") from exc
        if not isinstance(result, dict):
            raise PnrTrackingUnavailable("The authorized provider returned an invalid status response.")
        raw_status = str(result.get("status", "unknown")).lower()
        allowed = {item[0] for item in PnrTracker.STATUS_CHOICES}
        tracker.status = raw_status if raw_status in allowed else "unknown"
        tracker.last_error = ""
        tracker.last_checked_at = timezone.now()
        tracker.save(update_fields=("status", "last_error", "last_checked_at", "updated_at"))
        return Response(self.get_serializer(tracker).data)
