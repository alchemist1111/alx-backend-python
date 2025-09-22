from rest_framework import permissions
from rest_framework.exceptions import PermissionDenied

class IsParticipantOfConversation(permissions.BasePermission):
    """
    Custom permission to allow only participants of a conversation
    to send, view, update, or delete messages in that conversation.
    """

    def has_permission(self, request, view):
        # Only authenticated users can access the API
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        """
        Object-level permission:
        Allow actions only if the user is a participant in the conversation.
        """
        # Check that the conversation exists and the user is a participant in it
        conversation = obj.conversation
        if request.user not in conversation.participants.all():
            raise PermissionDenied("You are not a participant in this conversation.")
        return True
