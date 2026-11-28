from django.urls import path

from .views import WaitlistCoverageView, WaitlistImportView

urlpatterns = [
    path("waitlist/", WaitlistCoverageView.as_view(), name="waitlist-coverage"),
    path("waitlist/import/", WaitlistImportView.as_view(), name="waitlist-import"),
]
