import logging
from datetime import datetime
from django.http import HttpResponseForbidden

class RequestLoggingMiddleware:
    def __init__(self, get_response):
        """
        This method is called when the middleware is instantiated.
        The get_response is the next middleware or view to call.
        """
        self.get_response = get_response
        self.logger = logging.getLogger(__name__)
        
    def __call__(self, request):
        """
        This method is called for each request.
        It logs the user's request path and the timestamp.
        """
        # Get user information
        user = request.user.get_fullname if request.user.is_authenticated else 'Anonymous'
        
        # Log request data (timestamp, user, request path)
        log_message = f'{datetime.now()} - User: {user} - Path: {request.path}'
        
        # Log to the file
        with open('requests.log', 'a') as log_file:
            log_file.write(log_message + '\n')
        
        # Ensure the request continues to the next middleware/view
        response = self.get_response(request)
        
        return response  
    
class RestrictAccessByTimeMiddleware:
    def __init__(self, get_response):
        """
        Initializes the middleware. This method will be called when the middleware is instantiated.
        """
        self.get_response = get_response
        
    def __call__(self, request):
        """
        Checks the current time and restricts access to the chat outside the allowed time range (9 AM - 6 PM).
        """
        current_hour = datetime.now().hour # Get the current hour
        
        # If the current hour is outside the allowed range (not between 9 AM and 6 PM)
        if current_hour < 9 or current_hour >= 18:
            # Deny access to the chats
            return HttpResponseForbidden("Access to the chat is restricted to between 9 AM and 6 PM.")
        
        # If the time is within the allowed range, continue processing the request
        response = self.get_response
        return response          