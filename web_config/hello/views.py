from django.shortcuts import render
from django.http import HttpRequest, HttpResponse
from pymongo import MongoClient
import schedule
# Create your views here.

def home(request):
    data = {"First":'Oh','Second':'my God'}    
    return render(request,'hello/home.html/',context=data)

def view(request):
    data = {"First":request.GET['first'],'Second':request.GET['second']}    
    return render(request,'hello/view.html/',context=data)
def temp(request):
    return render(request,"hello/template.html")

def listFromMongoDB(request):
    data = request.GET.copy()
    with MongoClient("mongodb://172.17.0.3:27017") as my_client:
        my_db = my_client['my_db']
        result = list(my_db.movie_review.find().limit(30))
        data['page_obj'] = result
    return render(request,'hello/list.html',context=data)
