from django.shortcuts import render, redirect,resolve_url
from django.urls import reverse
from django.http import HttpResponse,HttpResponseRedirect
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import schedule,time
from pymongo import MongoClient
from django.views.decorators.csrf import csrf_exempt
# class for pagination 
from django.core.paginator import Paginator

#for goorm.io
from selenium.webdriver.chrome.options import Options

d_path = '/home/cho/Documents/Develop/web_config/driver/chromedriver_linux'
# Create your views here.


def login_page(request):
    return render(request,'job_list/login_listing.html')

@csrf_exempt
def job_list(request):    
    if (request.method == 'POST'):
        id = request.POST.get('id')
        pw = request.POST.get('pw')
        collectJobInfo(d_path,id,pw)
    with  MongoClient("mongodb://127.0.0.1:27017") as my_client:
        data = dict()
        job_info = list(my_client.my_db.job_info.find({}))
    paginator = Paginator(job_info,10)
    page_number = request.GET.get('page',1)
    data['page_obj'] = paginator.get_page(page_number)
    if len( data['page_obj']) != 0 :           
        return render(request,'job_list/list_page.html',context= data)
    else :
        return HttpResponse("<h1> 로그인을 하신 후 먼저 데이터를 채워주세요! <h1>")
    



# -------------------------------------------------- selenium ---------------------------------------------------------------
def login(id_1,password,driver):
    click = driver.find_element_by_css_selector('#header > div.top-area > div > div.util > a:nth-child(1)')
    click.click()
    id_info = driver.find_element_by_css_selector('#custId1')
    pw_info = driver.find_element_by_css_selector('#pwd1')
    button = driver.find_element_by_css_selector('#loginArea > div.login-form.login-idv > div.login-area > button')

    id_info.send_keys(id_1)
    pw_info.send_keys(password)
    button.click()

    

def close_tab(driver,url1):
    #time.sleep(1)
    if len(driver.window_handles) > 2 :

        for i in range(0,len(driver.window_handles)-1):
            driver.switch_to.window(driver.window_handles[-1])
            driver.close()  

        last_tab = driver.window_handles[-1]
        driver.switch_to.window(window_name=last_tab)
    else :  # 새 탭이 로딩이 완전히 되지않아서 데이터를 못 읽어오는 것을 방지 하기위한 조건문 
        i =0
        while driver.current_url != url1: # 현재 driver 의 링크와 구직정보를 제공하는 링크가 동일하지 않은경우 대기
            time.sleep(0.4)
            i+=1
            if i>5 :
                break
        last_tab = driver.window_handles[-1]            # 가장 최신단의 탭정보를 얻어옴
        driver.switch_to.window(window_name=last_tab)   # 최신단의 탭으로 이동
        last_tab = driver.window_handles[-1]            # 만약을 대비하기 위한 탭 이동코드
        driver.switch_to.window(window_name=last_tab)
        
        if driver.current_url != url1 :                 # 만약 위의 과정을 거쳐도 url 이 같지 않은경우 강제로 이동시킴
            driver.get(url=url1)

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
        try :
            con = [str(conditions[0].text).split('\n'),str(conditions[1].text).split('\n')]
            condition = f'{con[0][1]} | {con[1][1]}'         
        except Exception:
            con = [str(conditions[0].text).split('\n'),str(conditions[1].text).split('\n')]
            condition = f'{con[0]} | {con[1]}' 

        work = f"{section_down[0].text} | {section_down[1].text}"

   # print(f"{title} | {company} | {pay}")
    return [title,company,condition,pay,work]

def collectJobInfo(d_path,id_1,pw_1):    
    with  MongoClient("mongodb://127.0.0.1:27017") as my_client: 
        url = 'https://www.work.go.kr/seekWantedMain.do'
        my_client.my_db.job_info.drop()
     
        # for goorm.io setting selenium 
        # options = Options()
        # options.add_argument("--headless")
        # options.add_argument("--no-sandbox")

        # driver = webdriver.Chrome(options=options)          # for goorm.io 
        driver = webdriver.Chrome(executable_path=d_path) # for linux 

        driver.implicitly_wait(3) # 암묵적으로 웹 자원을 (최대) 3초 기다리기
        driver.get(url=url)

        # login 정보 입력 및 로그인
        login(id_1,pw_1,driver)
        time.sleep(3)
        close_tab(driver,url)
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
                link = info_link.get_attribute('href')
                d_day_tag = (td.find_elements_by_css_selector(' td:nth-child(5) > div > p'))
                d_day = d_day_tag[-1].text
                pay = str(td.find_element_by_css_selector('td:nth-child(4) > div > p:nth-child(1)').text).split('\n')
                career =  str(td.find_element_by_css_selector('td:nth-child(3) > div > p:nth-child(3) > em:nth-child(1)').text).split('\n')
                academic =  str(td.find_element_by_css_selector('td:nth-child(3) > div > p:nth-child(3) > em:nth-child(2)').text).split('\n')
                address =  str(td.find_element_by_css_selector('td:nth-child(3) > div > p:nth-child(3) > em:nth-child(3)').text).split('\n')
                info_link.click()

                # 새창으로 이동 
                close_tab(driver,link)

                # 데이터 수집
                list1 = get_data(driver)

                #print(list1)    
                # 새로 열렸던 창을 닫고 기존의 검색창으로 복귀 
                driver.close()   
                first_tab = driver.window_handles[0]
                driver.switch_to.window(window_name=first_tab )
                my_client.my_db.job_info.insert_one({'site':'worknet','title':list1[0],'company':list1[1],'link':link,'day_start':d_day[0],'day_end':d_day[1],'conditions':list1[2],'pay':list1[3],'desc':list1[4]})
            
            print(i)
            try :
                button = driver.find_element_by_css_selector(f"#CustmadeInfoMngVO > div > nav > a:nth-child({i+1})")
                button.click()
                print(f"page : {i+1}")
            except Exception :
                pass

        time.sleep(2)
        driver.quit()
