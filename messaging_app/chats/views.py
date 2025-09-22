from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status
from django_filters import rest_framework as filters
from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer
from .models import User
from rest_framework import permissions
from .permissions import IsOwner
from .permissions import IsParticipantOfConversation
from rest_framework.exceptions import PermissionDenied

# Filter class for filtering Conversations
class ConversationFilter(filters.FilterSet):
    created_after = filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Conversation
        fields = ['created_after', 'created_before']

class ConversationViewSet(viewsets.ModelViewSet):
    queryset = Conversation.objects.all()
    serializer_class = ConversationSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = ConversationFilter
    permission_classes = [permissions.IsAuthenticated]

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

# Filter class for filtering Messages
class MessageFilter(filters.FilterSet):
    sent_after = filters.DateTimeFilter(field_name='sent_at', lookup_expr='gte')
    sent_before = filters.DateTimeFilter(field_name='sent_at', lookup_expr='lte')

    class Meta:
        model = Message
        fields = ['sent_after', 'sent_before']

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    filter_backends = (filters.DjangoFilterBackend,)
    filterset_class = MessageFilter
    permission_classes = [permissions.IsAuthenticated, IsParticipantOfConversation, IsOwner]
    
    def get_queryset(self):
        """
        Return only the messages related to the logged-in user's conversations.
        """
        conversation_id = self.kwargs.get('conversation_id')
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise PermissionDenied("Conversation does not exist.")

    def perform_create(self, serializer):
        """
        Override to make sure the user is sending a message to a valid conversation.
        """
        conversation_id = self.kwargs.get('conversation_id')
        try:
            conversation = Conversation.objects.get(id=conversation_id)
        except Conversation.DoesNotExist:
            raise PermissionDenied("Conversation does not exist.")
        
        if self.request.user not in conversation.participants.all():
            raise PermissionDenied("You are not a participant in this conversation.")
        
        serializer.save(user=self.request.user, conversation=conversation)
