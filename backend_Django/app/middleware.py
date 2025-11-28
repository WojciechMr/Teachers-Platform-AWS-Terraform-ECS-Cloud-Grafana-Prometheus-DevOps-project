# app/middleware.py
from django.http import HttpResponse
from prometheus_client import Histogram
import time
request_latency = Histogram("django_request_latency_seconds", "Request latency in seconds (middleware)")

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
    

class PrometheusBeforeAfterMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.time()
        response = self.get_response(request)
        elapsed = time.time() - start_time
        request_latency.observe(elapsed)
        return response