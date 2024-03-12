from django.urls import include
from django.urls import path

urlpatterns = [
    path('', include('apps.accounts.urls')),
    path('', include('apps.locations.urls')),
]
