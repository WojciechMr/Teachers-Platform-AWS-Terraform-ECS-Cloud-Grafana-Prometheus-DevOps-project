# web/urls.py
from django.urls import path
from .views import home
from django.contrib import admin
from django.http import HttpResponse

def health_check(request):
    return HttpResponse("ok", status=200)

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('healthz', health_check),  # <--- dodany health check
]