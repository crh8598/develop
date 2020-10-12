from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
# Create your views here.

def home(request):
    data = {"First":'Oh','Second':'my God'}
    return render(request,'hello/home.html',context=data)