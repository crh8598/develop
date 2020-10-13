import pymongo
from pymongo import MongoClient

import requests
from bs4 import BeautifulSoup
import sqlite3
import time, datetime
import schedule


'''
    html - 구조 웹 콘텐트에 의미를 부여하고 구조를 형성
    css - 표현 시각화 디자인과 레이아웃 표현
    javascript - 행위 모든 front-end 브라우저 상호작용 담당

'''
def read_movie_review():
    #with  MongoClient("mongodb://172.17.0.3:27017") as my_client: #for linux
    with  MongoClient("mongodb://127.0.0.1:27017") as my_client: #for goorm_io
        my_db = my_client['my_db']

        url =  'https://movie.naver.com/movie/point/af/list.nhn?&page='
        #header = {'User-Agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.102 Safari/537.36'}
        header = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/85.0.4183.121 Safari/537.36'} # for linux
        index = list()
        total_page = 20
        for i in range(1,total_page):
            time.sleep(0.05)
            print(url+str(i))
            res = requests.get(url=(url+str(i)),headers=header)
            bts = BeautifulSoup(res.content,features='html5lib')
            table = bts.select('#old_content > table.list_netizen') # 영화 리뷰들이 담긴 테이블 추출
            table = table[0].find_all('tr')                         # 영화 리뷰가 담겨있는 tr 태그를 모두 추출
            for body in table[1:] :                                 # 첫번째 tr 은 head 부분이라 제외.

                time.sleep(0.05)
                name = body.a.get_text()                            # 영화 제목
                grade = body.em.get_text()                          # 영화 점수
                tes = body.find('td',{'class','title'})             # 영화 리뷰 및 제목이 담긴 title 태그 지정
                content = (tes.text.replace('\n','').replace('\t',''))[len(name)+13:-3] # 현 태그로부터 영화의 제목 길이 --> 실제 리뷰내용 --> 신고 텍스트 중에 실제 리뷰 내용만큼만 얻음

                num = (body.find('a',{'class':'author'}))   
                date = num.nextSibling.nextSibling
                my_db.movie_review.insert_one({"name":name,"grade":grade,"date":date,"page":i,"content":content})

        now = datetime.datetime.now()
        print(now)

schedule.every(10).seconds.do(read_movie_review)

while True:
    schedule.run_pending()
    
    time.sleep(1)
    

    

'''
CREATE TABLE reviews
(
  name    TEXT       NULL    ,
  grade   TEXT       NULL    ,
  date    MEDIUMTEXT NULL    ,
  page    TEXT       NULL    ,
  id      INTEGER   PRIMARY KEY   AUTOINCREMENT,
  content TEXT       NULL    
);
'''