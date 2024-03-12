from rest_framework.routers import DefaultRouter

from apps.location.api.views import LocationViewSet
from apps.location.api.views import StateViewSet

app_name = 'locations'

router = DefaultRouter()
# router.register(r'location_categories', , basename='location-categories')
router.register(r'locations', LocationViewSet, basename='locations')
router.register(r'states', StateViewSet, basename='states')

urlpatterns = [
    *router.urls,
]
