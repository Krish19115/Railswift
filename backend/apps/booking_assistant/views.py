from rest_framework import permissions, status, viewsets
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from .models import BookingPlan
from .serializers import BookingPlanReminderCreateSerializer, BookingPlanSerializer, BookingReminderSerializer


class BookingPlanViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = BookingPlanSerializer

    def get_queryset(self):
        return BookingPlan.objects.filter(user=self.request.user).select_related("source_station", "destination_station").prefetch_related("reminders")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(detail=True, methods=["post"], url_path="reminders")
    def reminders(self, request, pk=None):
        plan = self.get_object()
        if plan.status != "planned":
            raise ValidationError({"detail": "Reminders can only be added to planned journeys."})
        payload = BookingPlanReminderCreateSerializer(data=request.data)
        payload.is_valid(raise_exception=True)
        reminder = plan.reminders.create(user=request.user, **payload.validated_data)
        return Response(BookingReminderSerializer(reminder).data, status=status.HTTP_201_CREATED)
