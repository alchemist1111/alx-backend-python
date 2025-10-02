# messaging/tests.py

from django.test import TestCase
from django.contrib.auth.models import User
from .models import Message, Notification

class MessageNotificationTest(TestCase):

    def setUp(self):
        # Create users for testing
        self.sender = User.objects.create_user(full_name='sender', password='password123')
        self.receiver = User.objects.create_user(full_name='receiver', password='password123')

    def test_notification_creation_on_message_send(self):
        # Send a message from sender to receiver
        message = Message.objects.create(sender=self.sender, receiver=self.receiver, content="Hello, World!")

        # Check if a notification is created for the receiver
        notification = Notification.objects.get(user=self.receiver)
        self.assertEqual(notification.message, message)
        self.assertFalse(notification.seen) 
