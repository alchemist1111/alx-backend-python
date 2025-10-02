# messaging/views.py

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from django.contrib.auth import get_user_model

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

