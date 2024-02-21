from rest_framework.routers import DefaultRouter

from api.views import UserViewSets

app_name = 'user'

router = DefaultRouter()
router.register('', UserViewSets)

urlpatterns = [
    *router.urls,
]
