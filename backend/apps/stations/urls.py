from django.urls import path

from .views import StationListView

urlpatterns = [path("", StationListView.as_view(), name="station-list")]
