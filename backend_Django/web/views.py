# web/views.py
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_GET
def home(request):
    return HttpResponse("Witaj na edublinkier.com! 🚀")

@csrf_exempt
@require_GET
def health(request):
    return HttpResponse("OK", status=200)