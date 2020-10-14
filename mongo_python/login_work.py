from django.shortcuts import render
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import schedule,time
from pymongo import MongoClient


def login(id_1,password,driver):
    click = driver.find_element_by_css_selector('#header > div.top-area > div > div.util > a:nth-child(1)')
    click.click()
    id_info = driver.find_element_by_css_selector('#custId1')
    pw_info = driver.find_element_by_css_selector('#pwd1')
    button = driver.find_element_by_css_selector('#loginArea > div.login-form.login-idv > div.login-area > button')

    id_info.send_keys(id_1)
    pw_info.send_keys(password)
    button.click()

    

def close_tab(driver):
    if len(driver.window_handles) >= 4 :
        driver.switch_to.window(driver.window_handles[-1])
        driver.close()

        driver.switch_to.window(driver.window_handles[-1])
        driver.close()

        last_tab = driver.window_handles[-1]
        driver.switch_to.window(window_name=last_tab)
    else : 
        last_tab = driver.window_handles[-1]
        driver.switch_to.window(window_name=last_tab)

def get_data(driver):  
    # ---------------------------------- 직종 정보 구분 섹터 ------------------------------------------------
    try: 
        section_upper=driver.find_element_by_css_selector('#contents > div.careers-area > div.careers-new > div.border')
        section_down = driver.find_element_by_css_selector('#contents > div.careers-area > div:nth-child(6) > table > tbody > tr')

        # section_upper 에 해당하는 회사 상세 정보로부터 정보 습득.
        title = section_upper.find_element_by_css_selector('div.left > div.tit-area > p').text
        company = driver.find_element_by_css_selector('div.right > div.info > ul > li:nth-child(1) > div').text
        pay = section_upper.find_element_by_css_selector('div.left > div:nth-child(2) > div:nth-child(2) > div > ul > li:nth-child(2) > span').text
        conditions = section_upper.find_elements_by_css_selector('div.left > div:nth-child(2) > div:nth-child(1) > div > ul > li')
        condition = f'{conditions[0].text} | {conditions[1].text}'
        # section_down 에 있는 업무 데이터중 td 목록을 얻어와 정리
        table = driver.find_elements_by_css_selector('#contents > div.careers-area > div:nth-child(6) > table > tbody > tr > td')
        work = f"{table[0].text} | {table[1].text} | {table[2].text}"
    
    except Exception : 
    # 기존의 회사 정보와 다른 기업들이므로 이에대한 값들은 예외로 처리 
        section_upper=driver.find_element_by_css_selector('#contents > div.careers-area > div.careers-private')
        conditions = driver.find_elements_by_css_selector('#contents > div.careers-area > div:nth-child(5) > table > tbody > tr > td')
        section_down = driver.find_elements_by_css_selector('#contents > div.careers-area > div:nth-child(4) > table > tbody > tr> td')

        title = section_upper.find_element_by_css_selector('p.title').text
        company = section_upper.find_element_by_css_selector('table > tbody > tr:nth-child(1) > td:nth-child(2)').text
        pay = 'after meeting'
        condition = f'{conditions[0].text} | {conditions[1].text}'               
        work = f"{section_down[0].text} | {section_down[1].text}"

   # print(f"{title} | {company} | {pay}")
    return [title,company,condition,pay,work]

def collectJobInfo():
    #with  MongoClient("mongodb://172.17.0.3:27017") as my_client: #for linux
    with  MongoClient("mongodb://127.0.0.1:27017") as my_client: #for goorm_io
        url = 'https://www.work.go.kr/seekWantedMain.do'
        d_path = '../web_config/driver/chromedriver_linux'

        # Create your views here.
        driver = webdriver.Chrome(d_path)
        driver.implicitly_wait(3) # 암묵적으로 웹 자원을 (최대) 3초 기다리기
        driver.get(url=url)

        # login 정보 입력 및 로그인
        id_1 = input("id 를 입력해주세요 : ")
        pw_1 = input("pw 를 입력해주세요 : ")
        login(id_1,pw_1,driver)
        time.sleep(3)

        # 로그인 후 worknet 에 입력된 맞춤채용정보를 저장한 검색 페이지로 이동
        # 이때 seqNo 를 바꿔 지정된 검색 옵션을 선택할 수 있다. 현재는 2번을 사용중
        driver.get(url="https://www.work.go.kr/indivMemberSrv/custmadeInfoMng/custmadeInfoList.do?seqNo=2")

        # 페이지 정보 얻어오기 
        pageNo = driver.find_elements_by_css_selector('#CustmadeInfoMngVO > div > nav > a')
        
        # 페이지 수만큼 반복 실행
        for i in range(1,len(pageNo)+2):
            # 데이터 수집시작
            table = driver.find_element_by_css_selector("#CustmadeInfoMngVO > div > div:nth-child(7) > table > tbody")
            lists = table.find_elements_by_css_selector("tr")
            for td in lists :
                #새창으로 이동하기 위한 링크클릭
                info_link = td.find_element_by_css_selector('td:nth-child(3) > div > a')
                info_link.click()

                # 새창으로 이동 
                close_tab(driver)

                # 데이터 수집
                list1 = get_data(driver)
                #print(list1)    
                # 새로 열렸던 창을 닫고 기존의 검색창으로 복귀 
                driver.close()   
                first_tab = driver.window_handles[0]
                driver.switch_to.window(window_name=first_tab )
                my_client.my_db.job_info.insert_one({'title':list1[0],'company':list1[1],'conditions':list1[2],'pay':list1[3],'work':list1[4]})
            
            print(i)
            try :
                button = driver.find_element_by_css_selector(f"#CustmadeInfoMngVO > div > nav > a:nth-child({i+1})")
                button.click()
                print(f"page : {i+1}")
            except Exception :
                pass

        time.sleep(2)
        driver.quit()


if __name__ == "__main__":
    collectJobInfo()
'''
# 새창 접속
last_tab = driver.window_handles[-1]
driver.switch_to.window(window_name=last_tab)
# 새탭 종료하고 기존 탭으로 돌아가기
driver.close()   
first_tab = driver.window_handles[0]
driver.switch_to.window(window_name=first_tab )
'''