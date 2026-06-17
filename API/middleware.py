# API/middleware.py
import user_agents
from django.db import OperationalError, ProgrammingError
from django.utils import timezone
from API.models import Visitor, VisitorLog

# API/middleware.py
from django.http import JsonResponse
from django.conf import settings

class StatelessAPIMiddleware:
    """
    Globally intercepts any request starting with /api/.
    Forces Django to ignore CSRF checks and enforces our Bearer token.
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Only apply this logic to API routes
        if request.path.startswith('/api/'):
            
            # 1. Force Django's CSRF middleware to stand down
            setattr(request, '_dont_enforce_csrf_checks', True)
            
            # 2. Validate the Shared Secret Token from your frontend
            auth_header = request.headers.get('Authorization')
            expected_token = f"Bearer {settings.API_SHARED_SECRET}"
            
            if auth_header != expected_token:
                return JsonResponse({'error': 'Unauthorized API Access'}, status=401)
                
        # Let the request continue to the view
        response = self.get_response(request)
        return response

class VisitorTrackingMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            ip = self.get_client_ip(request) or "0.0.0.0"
            ua = request.META.get("HTTP_USER_AGENT", "")

            visitor, _ = Visitor.objects.get_or_create(
                ip_address=ip,
                defaults={"user_agent": ua}
            )

            visitor.total_requests += 1
            visitor.last_seen = timezone.now()
            visitor.save(update_fields=["total_requests", "last_seen"])

            VisitorLog.objects.create(
                visitor=visitor,
                path=request.path,
                method=request.method,
                referrer=request.META.get("HTTP_REFERER"),
                is_blog_detail="/post/" in request.path,
            )

        except (OperationalError, ProgrammingError):
            pass

        return self.get_response(request)

    def get_client_ip(self, request):
        x_forwarded = request.META.get("HTTP_X_FORWARDED_FOR")
        if x_forwarded:
            return x_forwarded.split(",")[0]
        return request.META.get("REMOTE_ADDR")
