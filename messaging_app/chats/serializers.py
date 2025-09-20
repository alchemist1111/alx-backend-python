from rest_framework import serializers
from .models import User, Conversation, Message
from rest_framework.exceptions import ValidationError
import uuid
import re

# User Serializer
class UserSerializer(serializers.ModelSerializer):
    first_name = serializers.CharField(max_length=255)
    last_name = serializers.CharField(max_length=255)
    email = serializers.EmailField(max_length=255)
    phone_number = serializers.CharField(max_length=20, allow_null=True, allow_blank=True)
    role = serializers.ChoiceField(choices=User.ROLE_CHOICES)
    
    full_name = serializers.serializerMethodField(read_only=True)
    class Meta:
        model = User
        fields = ['user_id', 'first_name', 'last_name', 'email', 'phone_number', 'role', 'created_at', 'updated_at']
     
    def get_full_name(self, obj):
        # Custom method to generate the full name dynamically
        return f'{obj.first_name} {obj.last_name}' 
     
    def validate_first_name(self, value):
         # Ensure first name is not empty and contains only alphabets
         if not value.isalpha():
             raise ValidationError('First name must contain only alphabetic characters.')
         return value
    
    def validate_last_name(self, value):
         # Ensure last name is not empty and contains only alphabets
         if not value.isalpha():
             raise ValidationError('Last name must contain only alphabetic characters.')
         return value 
        
    def validate_email(self, value):
        # Check if the email already exists in the database
        if User.objects.filter(email=value).exists():
            raise ValidationError('Email is already in use.')
        return value
    
    def validate_phone_number(self, value):
        # Validate phone number format using a regex.
        if value and not re.match(r'^\+?1?\d{9, 15}$', value):
            raise ValidationError('Phone number must be entered in the format: "+999999999". Up to 15 digits allowed.')
        return value
    
    def validate_role(self, value):
        # Ensure the role is one of the predifined choices
        if value not in dict(User.ROLE_CHOICES).keys():
            raise ValidationError(f'Role must be on of the following: {list(dict(User.ROLE_CHOICES).keys())}')
        return value
    
    def validate(self, data):
        # Object-level validation for complex logic involving multiple fields
        if not data.get('first_name') or not data.get('last_name'):
            raise ValidationError('Both first name and last name are required.')
        return data
        

        
# Message Serializer
class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)
    conversation = serializers.PrimaryKeyRelatedField(queryset=Conversation.objects.all(), write_only=True)
    message_body = serializers.TextField()
    
    class Meta:
        model = Message
        fields = ['message_id', 'sender', 'conversation', 'message_body', 'sent_at']
        read_only_fields = ['message_id', 'sent_at']   


# Conversation Serializer
class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Conversation
        fields = ['conversation_id', 'participants', 'messages', 'created_at', 'updated_at']
        read_only_fields = ['conversation_id', 'created_at', 'updated_at'] 
        
        
    def validate_conversation(self, value):
        # Custom validation to check if the user is a participant
        if self.context['request'].user not in value.participants.all():
            raise ValidationError('User is not a participant in this conversation.')
        return value               
        
                