from django.urls import path

from .views import TrainDetailView, TrainListView, TrainScheduleView, TrainsBetweenView

urlpatterns = [
    path("between/", TrainsBetweenView.as_view(), name="trains-between"),
    path("<str:number>/schedule/", TrainScheduleView.as_view(), name="train-schedule"),
    path("<str:number>/", TrainDetailView.as_view(), name="train-detail"),
    path("", TrainListView.as_view(), name="train-list"),
]
