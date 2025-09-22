# messaging_app/chats/permissions.py

from rest_framework import permissions

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only participants of a conversation
    to view, send, update, or delete messages.
    """
    
    def has_permission(self, request, view):
        # Only authenticated users can access the API
        return request.user and request.user.is_authenticated

class IsOwner(permissions.BasePermission):
    """
    Custom permission to check if the user is the owner of the message or conversation.
    """

    def has_object_permission(self, request, view, obj):
        # Check if the current user is the owner of the message or conversation
        return obj.user == request.user
    
    def has_object_permission(self, request, view, obj):
        """
        Object-level permission:
        Allow actions only if the user is a participant in the conversation.
        """
        # Assuming obj has a 'conversation' field with a 'participants' many-to-many field
        return request.user in obj.conversation.participants.all()