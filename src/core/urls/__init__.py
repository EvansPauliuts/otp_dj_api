import debug_toolbar
from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include
from django.urls import path
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView

from core.conf.environ import env

api = [
    path('v1/', include('core.urls.v1')),
]

urlpatterns = [
    path('api/', include(api)),
    path('healthchecks/', include('django_healthchecks.urls')),
    path(
        'api/schema/',
        SpectacularAPIView.as_view(api_version='0.1.0'),
        name='schema',
    ),
    path(
        'api/v1/doc/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
]


if env('DEBUG', cast=bool):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
