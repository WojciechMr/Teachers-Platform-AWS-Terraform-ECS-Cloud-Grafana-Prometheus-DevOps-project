# web/views.py
from django.http import JsonResponse, HttpResponse

def home(request):
    return HttpResponse("Witaj na edublinkier.com! 🚀")

def health(request):
    return JsonResponse({"status": "ok"})