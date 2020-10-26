import requests 
from bs4 import BeautifulSoup
import base64
import subprocess
from os.path  import basename
import urllib
#김밥
#url = 'https://m.gettyimagesbank.com/search/%EC%9D%B4%EB%AF%B8%EC%A7%80/%EA%B9%80%EB%B0%A5?lv=&st=union&page={}&q=%EA%B9%80%EB%B0%A5'
# 된장찌개
url = 'https://m.gettyimagesbank.com/search/%EC%9D%B4%EB%AF%B8%EC%A7%80/%EB%90%9C%EC%9E%A5%EC%B0%8C%EA%B0%9C?lv=&st=union&page={}&q=%EB%90%9C%EC%9E%A5%EC%B0%8C%EA%B0%9C'
header = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'} 

for i in range(1,8):
    res = requests.get(url=url.format(i),headers=header)
    bts = BeautifulSoup(res.content,'html5lib')
    table = bts.find_all('img',{'class':'thumbnail'})

    j = 1
    for src in table :
        print(src)
        imgUrl=src['src']       
        urllib.request.urlretrieve(imgUrl, ('./save/된장찌개/{}-{}.jpg'.format(i,j)))
        j+=1