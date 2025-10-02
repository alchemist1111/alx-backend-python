from django.db.models.signals import post_save
from django.db.models.signals import pre_save
from django.dispatch import receiver
from .models import Message, Notification, MessageHistory

@receiver(post_save, sender=Message)
def create_notification(sender, instance, created, **kwargs):
    if created: # Only trigger when a new message is created
        Notification.objects.create(
            user = instance.receiver,
            message = instance
        )
        
@receiver(pre_save, sender=Message)
def log_message_edit(sender, instance, **kwargs):
    # Check if the message content is being edited (not the first creation)
    if instance.pk:
        try:
            original = Message.objects.get(pk=instance.pk) # Original content
            
            if original.content != instance.content:  # Check if content is different
                # Create a new history record for the edited message
                MessageHistory.objects.create(
                    message = original,
                    old_content=original.content
                )   
                instance.edited = True # Mark the message as edited
        except Message.DoesNotExist:
            pass      # If the message does not exist, do nothing     