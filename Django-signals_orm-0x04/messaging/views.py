# messaging/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model
from .serializers import MessageSerializer
from .models import Message
from django.shortcuts import get_object_or_404

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
    permission_classes = [IsAuthenticated]

    def get_replies(self, parent_message):
        """
        Recursive function to fetch all replies to a message and its nested replies.
        """
        replies = parent_message.replies.all()  # Get all replies to the current message
        result = []

        # For each reply, serialize it and add any nested replies
        for reply in replies:
            reply_data = MessageSerializer(reply).data  # Serialize the reply
            reply_data['replies'] = self.get_replies(reply)  # Recursively get nested replies
            result.append(reply_data)

        return result

    def get(self, request, message_id, *args, **kwargs):
        # Fetch the root message (the one being replied to) using select_related and prefetch_related
        message = get_object_or_404(
            Message.objects.prefetch_related('replies').select_related('sender', 'receiver'),
            id=message_id
        )

        # Serialize the message and its replies recursively
        message_data = MessageSerializer(message).data
        message_data['replies'] = self.get_replies(message)  # Add replies in a nested format
        
        return Response(message_data, status=status.HTTP_200_OK)

    def post(self, request, *args, **kwargs):
        """
        This view allows users to send a reply to a specific message.
        """
        sender = request.user  # Get the sender (currently logged-in user)
        receiver = get_object_or_404(User, id=request.data.get('receiver_id'))
        parent_message = get_object_or_404(Message, id=request.data.get('parent_message_id'))

        # Create a new message (reply)
        new_message = Message.objects.create(
            sender=sender,
            receiver=receiver,
            content=request.data.get('content'),
            parent_message=parent_message  # Set the parent message as the one being replied to
        )

        return Response(MessageSerializer(new_message).data, status=status.HTTP_201_CREATED)    


class UnreadMessagesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Fetch unread messages for the logged-in user using filter() and only() for optimization
        unread_messages = Message.objects.filter(receiver=request.user, read=False).only('id', 'sender', 'content', 'timestamp')

        # Serialize the unread messages
        serializer = MessageSerializer(unread_messages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)      

