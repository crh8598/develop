from django.shortcuts import render
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
import schedule,time
from pymongo import MongoClient
import requests
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.common.exceptions import ElementNotVisibleException
 

# 로그인을 위한 함수
def login(id_1,password,driver):
    click = driver.find_element_by_css_selector('#header > div.top-area > div > div.util > a:nth-child(1)')
    click.click()
    id_info = driver.find_element_by_css_selector('#custId1')
    pw_info = driver.find_element_by_css_selector('#pwd1')
    button = driver.find_element_by_css_selector('#loginArea > div.login-form.login-idv > div.login-area > button')

    id_info.send_keys(id_1)
    pw_info.send_keys(password)
    button.click()
    time.sleep(3)
    print('Loggined successfully!')

#worknet 링크로 부터 주소정보를 읽는 함수
def get_data(driver,pas):  
    # ---------------------------------- 직종 정보 구분 섹터 ------------------------------------------------
    if pas == 1 :
        # section_upper 에 해당하는 회사 상세 정보로부터 정보 습득.
        try :
            section_upper=driver.find_element_by_css_selector('#contents > div.careers-area > div.careers-new > div.border')
            address = section_upper.find_element_by_css_selector('div.left > div:nth-child(2) > div:nth-child(2) > div > ul > li:nth-child(1) > span').text
        except Exception :
            address = ''
            pass
            
    else :
        try : #공채사이트가 회사정보만 있는경우 
            address = driver.find_element_by_css_selector('#wrapper > div > div > div > div > div.cont-area > div > div > ul > li:nth-child(1) > span').text            
        
        except Exception: #공채사이트가 기존의 사이트와 동일한 경우
            # section_upper 에 해당하는 회사 상세 정보로부터 정보 습득.
            
            section_upper=driver.find_element_by_css_selector('#contents > div.careers-area > div.careers > div.cont-area > div > div > ul > li:nth-child(1) > span')
            address = section_upper.text                
    return address
        
    
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

def collectJobInfo():
    #with  MongoClient("mongodb://172.17.0.3:27017") as my_client: #for linux
    #header = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
    #header = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'} #for windows
    
    url = '''\
    https://www.work.go.kr/empInfo/empInfoSrch/list/dtlEmpSrchList.do?careerTo=&keywordJobCd=&occupation=&rot2WorkYn=&templateInfo=&payGbn=&\
    resultCnt=50&keywordJobCont=N&cert=&cloDateStdt=&moreCon=more&minPay=&codeDepth2Info=11000&isChkLocCall=&sortFieldInfo=DATE&major=&resrDutyExcYn=&\
    sortField=DATE&staArea=&sortOrderBy=DESC&keyword=&termSearchGbn=all&benefitSrchAndOr=O&disableEmpHopeGbn=&webIsOut=&actServExcYn=&keywordStaAreaNm=N&m\
    axPay=&emailApplyYn=&listCookieInfo=DTL&pageCode=&codeDepth1Info=11000&keywordEtcYn=&publDutyExcYn=&keywordJobCdSeqNo=&exJobsCd=&templateDepthNmInfo=&\
    computerPreferential=&regDateStdt=&employGbn=&empTpGbcd=1&region=&resultCntInfo=50&siteClcd=all&cloDateEndt=&sortOrderByInfo=DESC&currntPageNo=1&indArea=&\
    careerTypes=&searchOn=Y&subEmpHopeYn=&academicGbn=&foriegn=&templateDepthNoInfo=&mealOfferClcd=&station=&moerButtonYn=Y&holidayGbn=&\
    enterPriseGbn=01%7C04%7C08%7C20&academicGbnoEdu=noEdu&cloTermSearchGbn=all&keywordWantedTitle=N&stationNm=&benefitGbn=&keywordFlag=&essCertChk=&\
    isEmptyHeader=&depth2SelCode=&_csrf=dd0e5b2f-27ad-42c0-8a64-925e7876ed19&keywordBusiNm=N&preferentialGbn=all&rot3WorkYn=&pfMatterPreferential=&\
    regDateEndt=&staAreaLineInfo1=11000&staAreaLineInfo2=1&pageIndex={}&termContractMmcnt=&careerFrom=&laborHrShortYn=#viewSPL\
    '''.replace('        ','').replace('    ','')
    d_path = '../web_config/driver/chromedriver_linux' # for linux
    #d_path = 'C:/크롤러/driver/chromedriver86.exe' #for windows
    print("start reading!")


    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--headless')
    options.add_argument('window-size=1920x1080')
    options.add_argument("disable-gpu")

    driver = webdriver.Chrome(d_path,options=options)
    driver.implicitly_wait(10) # 암묵적으로 웹 자원을 (최대) 20초 기다리기

    with  MongoClient("mongodb://127.0.0.1:27017") as my_client:
        #데이터 중복방지용 콜렉션 드랍
        my_client.Jobinfo.Joblist.drop()
          
        
        # worknet 로그인 및 새창 닫기
        driver.get(url='https://www.work.go.kr/seekWantedMain.do')
        login('whrnrgusdlek','dhfl108!',driver)        
     
        close_tab(driver,driver.current_url)
        # 상세 검색 첫페이지로 이동 
        driver.get(url=url.format('1'))

        # 페이지 정보 얻어오기 
        pageNo = driver.find_elements_by_css_selector('#mForm > div.nav_wrp > div')[0].text[2:-5]

        # 페이지 수만큼 반복 실행 i: 페이지 j : 리스트 
        # i for 문 내에서 j를 증가시켜서 어떤 리스트를 얻어오는 지 알 수 있게 설정하였음
        for i in range(1,int(pageNo)+1):
            time.sleep(3)

            # 데이터가 담긴 테이블 정보 리딩
            tr_table = driver.find_elements_by_css_selector("#mForm > div.table-wrap > table > tbody > tr")
            j = 1
            for tr in tr_table:
                #새창으로 이동하기 위한 링크클릭
                #time.sleep(3)
                

                # 만약 탭창이 안닫혀 있으면 이를 닫고 기존 리스트가 담긴 첫번째 탭으로 이동
                if len(driver.window_handles) > 1 :
                    close_tab(driver,url.format(str(i)))
                elif driver.current_url != url.format(str(i)) :
                    driver.implicitly_wait(20)
                else : 
                    pass
                
               
              
                exc = str(tr.find_element_by_css_selector('td:nth-child(2) > div > span').text).replace(' ','')
             
                # 공채 사이트 외에 정보를 읽어올 경우의 태그정보
                                
                #공채 형태의 데이터를 읽어올 경우의 태그정보
                if exc == '알리오':
                    company_tag = driver.find_element_by_css_selector(f'#list{j} > td:nth-child(2)') 
                    title_link = driver.find_element_by_css_selector(f'#list{j} > td:nth-child(3) > div > div > a')
                    company = str(company_tag.text).replace('\n','').replace('\t','').replace('\r','')
                    title = str(title_link.text).replace('\n','').replace('\t','').replace('\r','')
                    pas = 2
                else :
                    try :
                        company_tag = tr.find_element_by_css_selector('td:nth-child(2) > a') 
                        title_link = tr.find_element_by_css_selector('td:nth-child(3) > div > div > a')
                        company = company_tag.text
                        title = title_link.text
                        pas = 1
                    except Exception :
                        company_tag = driver.find_element_by_css_selector(f'#list{j} > td:nth-child(2)') 
                        title_link = driver.find_element_by_css_selector(f'#list{j} > td:nth-child(3) > div > div > a')
                        company = str(company_tag.text).replace('\n','').replace('\t','').replace('\r','')
                        title = str(title_link.text).replace('\n','').replace('\t','').replace('\r','')
                        pas = 2
                    
                work = tr.find_element_by_css_selector('td:nth-child(3) > div > p').text     
                link = title_link.get_attribute('href')

                 # 새창이 뜨는 공채 속보는 예외 
                if exc == '공채속보':                    
                    address = tr.find_elements_by_xpath(f'//*[@id="list{j}"]/td[3]/div/p[2]/em')[-1].text
                    my_client.Jobinfo.Joblist.insert_one({'company':company,'address':address,'title':title,'link':link,'work':work})
                    print(f'{i} Page , {j} list, from {exc}')
                    j+=1
                    continue
                
                
                title_link.click()      #공채 정보 링크를 클릭                
                close_tab(driver,link)  #주소정보를 얻기위한 방법 
                address = get_data(driver,pas)                                                                            
            
                # 새탭으로 열린 창을 닫고 구직정보 리스트를 제공하는 본래 링크로 이동
                driver.close()   
                first_tab = driver.window_handles[0]
                driver.switch_to.window(window_name=first_tab)

                # URL 확인
                if driver.current_url != url.format(str(i)) :
                    driver.get( url.format(str(i)))      # 새로 열렸던 창을 닫고 기존의 검색창으로 복귀  
                                                           
                my_client.Jobinfo.Joblist.insert_one({'company':company,'address':address,'title':title,'link':link,'work':work})
                print(f'{i} Page , {j} list, from {exc}')
                j+=1
                
                    

            driver.get(url=url.format(str(i+1)))


        
    driver.quit()


#schedule.every(24).hours.do(collectJobInfo)

if __name__ == "__main__":
    #schedule.run_pending()
    #time.sleep(1)
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