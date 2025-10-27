from django.urls import path
from . import views

urlpatterns = [
    path("health/", views.health),  # opcjonalne, middleware i tak zwraca 200
    path("", views.home),
]
