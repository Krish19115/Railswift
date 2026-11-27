from rest_framework.routers import DefaultRouter

from .views import SavedJourneyViewSet

router = DefaultRouter()
router.register("", SavedJourneyViewSet, basename="saved-journey")
urlpatterns = router.urls
