from rest_framework import permissions


class IsAdminOrSelf(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return request.user.is_authenticated and (request.user.is_superuser or obj == request.user)


class IsSuperuserOrTechDir(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and (request.user.is_superuser or request.user.position == 'techDir')
