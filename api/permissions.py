from rest_framework.permissions import BasePermission, SAFE_METHODS

class IsAdminOrReadOnly(BasePermission):
    """
    Custom permission: only admins can edit; others can read only.
    """

    def has_permission(self, request, view):
        if request.method in SAFE_METHODS:
            return True
        return request.user and request.user.is_staff  # or use `is_superuser` if you prefer
        # return bool(request.user and request.user.is_authenticated and request.user.is_staff)
