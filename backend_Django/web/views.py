# web/views.py
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

def home(request):
    return HttpResponse("Witaj na edublinkier.com! 🚀")

@csrf_exempt
def health(request):
    """
    Minimalny endpoint dla ALB Health Check
    """
    return HttpResponse(status=200)