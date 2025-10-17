# web/urls.py
from django.http import HttpResponse
from django.urls import path

# Funkcja health check
def health_check(request):
    return HttpResponse("ok", status=200)

# Istniejące URL patterns
from .views import home
from django.contrib import admin

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
]

# Dodajemy health check
urlpatterns += [
    path("healthz", health_check),
]
