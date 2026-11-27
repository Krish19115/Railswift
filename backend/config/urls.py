from django.contrib import admin
from django.urls import include, path


urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/", include("apps.core.urls")),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/stations/", include("apps.stations.urls")),
    path("api/v1/trains/", include("apps.trains.urls")),
    path("api/v1/saved-journeys/", include("apps.journeys.urls")),
]
