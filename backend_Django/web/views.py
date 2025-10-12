# web/views.py
from django.http import HttpResponse

def home(request):
    return HttpResponse("Witaj na edublinkier.com! 🚀")