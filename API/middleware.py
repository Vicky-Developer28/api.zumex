# API/middleware.py
import user_agents
from django.db import OperationalError, ProgrammingError
from django.utils import timezone
from API.models import Visitor, VisitorLog


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
