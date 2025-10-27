# app/middleware.py
from django.http import HttpResponse


class HealthCheckBypassHostMiddleware:
    """
    Middleware zwracający 200 OK dla /health/,
    zanim Django sprawdzi Host header (fix dla ALB health checks).
    """
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.path == "/health/":
            return HttpResponse("OK", status=200)
        return self.get_response(request)