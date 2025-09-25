import logging
from datetime import datetime

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
        with open('request.log', 'a') as log_file:
            log_file.write(log_message + '\n')
        
        # Ensure the request continues to the next middleware/view
        response = self.get_response(request)
        
        return response      