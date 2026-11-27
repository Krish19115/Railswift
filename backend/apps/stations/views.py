from django.db.models import Q
from rest_framework import generics
from rest_framework.permissions import AllowAny

from .models import Station
from .serializers import StationSerializer


class StationListView(generics.ListAPIView):
    permission_classes = [AllowAny]
    serializer_class = StationSerializer

    def get_queryset(self):
        queryset = Station.objects.filter(is_active=True)
        query = self.request.query_params.get("search", "").strip()
        if query:
            queryset = queryset.filter(
                Q(code__istartswith=query) | Q(name__icontains=query) | Q(city__icontains=query)
            )
        return queryset.order_by("name")[:20]
