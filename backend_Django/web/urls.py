# web/urls.py
from django.urls import path
from .views import home
from django.contrib import admin


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
]