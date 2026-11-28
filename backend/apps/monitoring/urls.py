from rest_framework.routers import DefaultRouter

from .views import PnrTrackerViewSet

router = DefaultRouter()
router.register("", PnrTrackerViewSet, basename="pnr-tracker")

urlpatterns = router.urls
