from rest_framework.permissions import (
    AllowAny,
    BasePermission,
    IsAuthenticated,
    DjangoModelPermissions,
)

class SuperUserOnly(BasePermission):
    def has_permission(self, request, view):
        return request.user.is_superuser


class CustomObjectPermissions(DjangoModelPermissions):
    perms_map = {
        'GET': ['%(app_label)s.view_%(model_name)s'],
        'OPTIONS': ['%(app_label)s.view_%(model_name)s'],
        'HEAD': ['%(app_label)s.view_%(model_name)s'],
        'POST': ['%(app_label)s.add_%(model_name)s'],
        'PUT': ['%(app_label)s.change_%(model_name)s'],
        'PATCH': ['%(app_label)s.change_%(model_name)s'],
        'DELETE': ['%(app_label)s.delete_%(model_name)s'],
    }


__all__ = [
    'AllowAny',
    'CustomObjectPermissions',
    'IsAuthenticated',
    'SuperUserOnly',
]
