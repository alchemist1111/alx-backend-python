from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from .models import User, Conversation, Message
from .serializers import UserSerializer, ConversationSerializer, MessageSerializer

# Conversation Viewset
class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    
    def perform_create(self, serializer):
        # Create a conversation and add participants
        conversation = serializer.save()
        participants = self.request.data.get("participants", [])
        for user_id in participants:
            user = User.objects.get(user_id=user_id)
            conversation.participants.add(user)
    
    @action(detail=True, methods=['post'])
    def send_message(self, request, pk=None):
        conversation = self.get_object()
        serializer = MessageSerializer(data=request.data)
        
        if serializer.is_valid():
            serializer.save(sender=request.user, conversation=conversation)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)    


# Message viewset
class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer

    def perform_create(self, serializer):
        conversation = serializer.validated_data['conversation']
        # Ensure the sender is assigned from the authenticated user
        serializer.save(sender=self.request.user, conversation=conversation)        
            
                    
