from django.shortcuts import render, HttpResponse

def index(request):
    #return HttpResponse("WELCOME TO PMS")
    return render(request, 'index.html');
# Create your views here.
