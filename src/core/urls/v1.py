from django.urls import path, include

urlpatterns = [
    # path('users/', include('apps.users.urls')),
    path('', include('apps.accounts.urls')),
]
