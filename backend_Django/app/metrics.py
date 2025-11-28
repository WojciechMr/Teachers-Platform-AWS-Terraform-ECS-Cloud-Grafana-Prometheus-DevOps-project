from prometheus_client import Counter, Histogram
from functools import wraps
from .metrics import request_latency

# Liczniki akcji
login_counter = Counter("django_login_total", "Total number of logins")
registration_counter = Counter("django_registration_total", "Total number of registrations")
lesson_gen_counter = Counter("django_lesson_generated_total", "Total lessons generated")
quiz_gen_counter = Counter("django_quiz_generated_total", "Total quizzes generated")

# Histogram dla czasu requestów
request_latency = Histogram("django_request_latency_seconds", "Request latency in seconds")

def track_latency(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        with request_latency.time():
            return view_func(request, *args, **kwargs)
    return wrapper