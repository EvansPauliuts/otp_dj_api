from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'location_categories', {}, basename='location-categories')
router.register(r'locations', {}, basename='locations')
router.register(r'states', {}, basename='states')

urlpatterns = [
    *router.urls,
]
