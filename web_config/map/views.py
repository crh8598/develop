from django.shortcuts import render
import folium
# Create your views here.
import requests,json
from bs4 import BeautifulSoup

KakaoAK ='KakaoAK 876e9dd3cee1b67c2f15c6a58cd44f9c'

def map(request):
    lat_long=[35.3369,127.7306]
    m = folium.Map(lat_long,zoom_start=10)
    popText = folium.Html('<b>jirisan</b> </br>'+str(lat_long),script=True)
    popup = folium.Popup(popText,max_width=2650)
    folium.RegularPolygonMarker(location=lat_long,popup=popup).add_to(m) # 맵의 지정된 좌표에 마름모 꼴의 표기를 하는데 팝업을 해줌
    m = m._repr_html_() # 이 작업을 해 줌으로서 html 에서 사용할 수 있도록 구성을 바꿔주는 것.

    
    datas=  {'mountain_map':m}



    return render(request,'map/jirisan.html',context=datas)

    