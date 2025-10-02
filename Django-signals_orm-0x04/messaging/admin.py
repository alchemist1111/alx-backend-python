from django.contrib import admin
from .models import Message, Notification

# Register your models here.
@admin.register(Message)
class MessageAdmin(admin.ModelAdmin):
    list_display = ('sender', 'receiver', 'timestamp', 'content')
    

@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('user', 'message', 'seen', 'created_at')
    list_filter = ('seen',)    
