# messaging_app/chats/permissions.py

from rest_framework import permissions

class IsOwner(permissions.BasePermission):
    """
    Custom permission to check if the user is the owner of the message or conversation.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the current user is the owner of the message or conversation
        return obj.user == request.user