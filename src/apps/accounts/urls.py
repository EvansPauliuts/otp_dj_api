from core.conf.environ import env
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path
from rest_framework.routers import DefaultRouter

from apps.accounts.api.views import GroupViewSet
from apps.accounts.api.views import JobTitleViewSet
from apps.accounts.api.views import PermissionViewSet
from apps.accounts.api.views import ResetPasswordView
from apps.accounts.api.views import TokenProvisionView
from apps.accounts.api.views import UpdateEmailView
from apps.accounts.api.views import UpdatePasswordView
from apps.accounts.api.views import UserDetailView
from apps.accounts.api.views import UserLogoutView
from apps.accounts.api.views import UserViewSet

app_name = 'users'

router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('job_titles', JobTitleViewSet, basename='job_titles')
router.register('groups', GroupViewSet, basename='groups')
router.register('permissions', PermissionViewSet, basename='permissions')

urlpatterns = [
    path(
        'change_password/',
        UpdatePasswordView.as_view(),
        name='change_password',
    ),
    path(
        'reset_password/',
        ResetPasswordView.as_view(),
        name='reset_password',
    ),
    path(
        'change_email/',
        UpdateEmailView.as_view(),
        name='change_email',
    ),
    path(
        'login/',
        TokenProvisionView.as_view(),
        name='provision_token',
    ),
    path('logout/', UserLogoutView.as_view(), name='logout'),
    path('me/', UserDetailView.as_view(), name='me'),
    *router.urls,
]

if env('DEBUG'):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

admin.site.site_header = 'Evans TMS Administration'
admin.site.site_title = 'Evans TMS Administration'
admin.site.index_title = 'Evans TMS Administration'
admin.site.empty_value_display = 'N/A'
