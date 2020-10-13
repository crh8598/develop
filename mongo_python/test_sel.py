from django.shortcuts import render
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import schedule,time
import pymongo


def search_keywork(url,keyword):
    search_box = driver.find_element_by_css_selector("#topQuery")
    search_form = driver.find_element_by_css_selector("#searchFrm > div.header-search > div.searc-area > button")

    search_box.send_keys(keyword)
    search_form.click()
    return 0


keywords = ['임베디드 드론','임베디드 개발자']
url = 'https://www.work.go.kr/seekWantedMain.do'
d_path = '../web_config/driver/chromedriver_linux'
# Create your views here.
driver = webdriver.Chrome(d_path)
driver.implicitly_wait(3) # 암묵적으로 웹 자원을 (최대) 3초 기다리기

driver.get(url="https://www.work.go.kr/seekWantedMain.do")

for keyword in keywords:
    search_keywork(url,keyword)

    add_list = driver.find_element_by_css_selector("#gnb > ul > li.curr > a")
    add_list.click()

    job_lists = driver.find_element_by_css_selector("#contents > div > div.top > div.left-section > div:nth-child(2) > div.result-recruit-list > ul")
    #print(job_lists.text)

    for arr in job_lists.find_elements_by_tag_name('li'):
        title = arr.find_element_by_tag_name('a').text
        company = arr.find_element_by_css_selector("div.top > div > div.txt > span").text
        condition = arr.find_elements_by_css_selector('div.top > div > div.cp-info > p:nth-child(1) > span')
        address = arr.find_element_by_css_selector('div.top > div > div.cp-info > p:nth-child(2) > span:nth-child(1)').text

        print("제목 :",title,"회사명 :", company)
        print("조건 : ",f"{condition[0].text}, {condition[3].text}, {condition[1].text} ")
        print("주소 :",address )


    # div.top > div > div.cp-info > p:nth-child(2) > span:nth-child(1)

    time.sleep(3)
    driver.quit()



'''
# 새창 접속
last_tab = driver.window_handles[-1]
driver.switch_to.window(window_name=last_tab)
# 새탭 종료하고 기존 탭으로 돌아가기
driver.close()   
first_tab = driver.window_handles[0]
driver.switch_to.window(window_name=first_tab )
'''