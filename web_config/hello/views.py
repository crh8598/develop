from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
# Create your views here.

def home(request):
    data = {"First":'Oh','Second':'my God'}    
    return render(request,'hello/home.html/',context=data)

def view(request):
    data = {"First":request.GET['first'],'Second':request.GET['second']}    
    return render(request,'hello/view.html/',context=data)
