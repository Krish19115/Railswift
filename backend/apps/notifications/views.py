from rest_framework import generics, permissions

from .models import NotificationLog
from .serializers import NotificationLogSerializer


class NotificationListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationLogSerializer

    def get_queryset(self):
        return NotificationLog.objects.filter(user=self.request.user)[:100]
