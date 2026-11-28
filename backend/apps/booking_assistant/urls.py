from rest_framework.routers import DefaultRouter

from .views import BookingPlanViewSet

router = DefaultRouter()
router.register("", BookingPlanViewSet, basename="booking-plan")
urlpatterns = router.urls
