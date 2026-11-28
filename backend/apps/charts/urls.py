from django.urls import path

from .views import ChartQueryView, LatestChartView

urlpatterns = [
    path("", ChartQueryView.as_view(), name="chart-query"),
    path("<int:snapshot_id>/", LatestChartView.as_view(), name="chart-detail"),
]
