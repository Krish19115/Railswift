from django.urls import path

from .views import ConfirmationPredictionView, ModelMetricsView, ModelStatusView, PredictionHistoryView

urlpatterns = [
    path("confirmation/", ConfirmationPredictionView.as_view(), name="confirmation-prediction"),
    path("history/", PredictionHistoryView.as_view(), name="prediction-history"),
    path("status/", ModelStatusView.as_view(), name="prediction-model-status"),
    path("metrics/", ModelMetricsView.as_view(), name="prediction-metrics"),
]
