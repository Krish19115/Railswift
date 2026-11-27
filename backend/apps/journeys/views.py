from rest_framework import permissions, viewsets

from .models import SavedJourney
from .serializers import SavedJourneySerializer


class SavedJourneyViewSet(viewsets.ModelViewSet):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = SavedJourneySerializer

    def get_queryset(self):
        return SavedJourney.objects.filter(user=self.request.user).select_related("source_station", "destination_station")

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
