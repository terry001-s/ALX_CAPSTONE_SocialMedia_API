from rest_framework import permissions

class IsPublicEndpoint(permissions.BasePermission):
    """
    Allow access to everyone (for login/register).
    """
    def has_permission(self, request, view):
        # Allow all requests
        return True


class IsOwnerOrReadOnly(permissions.BasePermission):
    """
    Only allow owners to edit their objects.
    """
    def has_object_permission(self, request, view, obj):
        # Read permissions are allowed to any request
        if request.method in permissions.SAFE_METHODS:
            return True
        
        # Write permissions are only allowed to the owner
        return obj == request.user