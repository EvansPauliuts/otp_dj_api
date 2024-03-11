from rest_framework import permissions

class ViewAllUsersPermissions(permissions.BasePermission):
    def has_permission(self, request, view):
        if view.action == 'retrieve':
            return True

        return request.user.has_perm('accounts.view_all_users') or request.user.is_superuser


class OwnershipPermissions(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.user and request.user.is_superuser:
            return True
        return obj == request.user
