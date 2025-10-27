from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt

@csrf_exempt
def health(request):
    return HttpResponse("OK", status=200)

def home(request):
    return HttpResponse("the platform is currently under renovation, the official monthly Open Source is scheduled for December, Welcome!")
