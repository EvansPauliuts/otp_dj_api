import debug_toolbar
from django.contrib import admin
from django.urls import include
from django.urls import path
from drf_spectacular.views import SpectacularAPIView
from drf_spectacular.views import SpectacularSwaggerView

api = [
    path('v1/', include('core.urls.v1')),
]

urlpatterns = [
    path('api/', include(api)),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path(
        'api/v1/doc/',
        SpectacularSwaggerView.as_view(url_name='schema'),
        name='swagger-ui',
    ),
    path('admin/', admin.site.urls),
    path('__debug__/', include(debug_toolbar.urls)),
]
