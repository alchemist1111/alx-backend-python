from django.urls import path
from .views import DeleteUserView

urlpatterns = [
    path('delete_user/', DeleteUserView.as_view(), name='delete_user'),
]
