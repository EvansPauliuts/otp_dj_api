from django.urls import include, path
from rest_framework.routers import DefaultRouter

from api.views import UserViewSets

app_name = 'user'

router = DefaultRouter()
router.register('', UserViewSets)

urlpatterns = [
    path('', include(router.urls)),
]
