from django.urls import path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenVerifyView, TokenRefreshView

from apps.users.api.views import (
    FileViewSet,
    AuthViewSets,
    ImageViewSet,
    UserViewSets,
    PasswordChangeView,
    CustomObtainTokenPairView,
)

app_name = 'users'
router = DefaultRouter()

router.register('', UserViewSets)
router.register('', AuthViewSets, basename='auth')
router.register('change-password', PasswordChangeView, basename='password_change')
router.register('file', FileViewSet, basename='file')
router.register('image', ImageViewSet, basename='image')

urlpatterns = [
    path('login/', CustomObtainTokenPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='refresh-token'),
    path('token/verify/', TokenVerifyView.as_view(), name='verify-token'),
    *router.urls,
]
