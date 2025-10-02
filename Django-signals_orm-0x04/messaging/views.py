# messaging/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import MessageSerializer
from .models import Message

User = get_user_model()

class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete_user(self, request, *args, **kwargs):
        user = request.user  # The logged-in user
        try:
            user.delete()  # This will trigger the post_delete signal for the User model
            return Response({"detail": "User account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            return Response({"detail": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ThreadedConversationView(APIView):
    
    def get_replies(self, parent_message):
        """Recursive method to fetch all replies for a given parent message."""
        replies = parent_message.replies.all()  # Get all replies to the message
        result = []
        for reply in replies:
            reply_data = MessageSerializer(reply).data  # Serialize the reply
            # Recursively fetch replies to this reply (nested replies)
            reply_data['replies'] = self.get_replies(reply)
            result.append(reply_data)
        return result

    def get(self, request, message_id, *args, **kwargs):
        # Fetch the message and its replies efficiently using prefetch_related
        message = Message.objects.prefetch_related('replies').select_related('sender', 'receiver').get(id=message_id)
        
        # Serialize the message and its replies
        message_data = MessageSerializer(message).data
        message_data['replies'] = self.get_replies(message)
        
        return Response(message_data, status=status.HTTP_200_OK)        

