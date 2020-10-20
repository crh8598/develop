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
def get_data(driver):  
    # ---------------------------------- 직종 정보 구분 섹터 ------------------------------------------------

    section_upper=driver.find_element_by_css_selector('#contents > div.careers-area > div.careers-new > div.border')    

    # section_upper 에 해당하는 회사 상세 정보로부터 정보 습득.
    address = section_upper.find_element_by_css_selector('div.left > div:nth-child(2) > div:nth-child(2) > div > ul > li:nth-child(1) > span').text
   # print(f"{title} | {company} | {pay}")
    return address
    
def close_tab(driver):
    #time.sleep(1)
    if len(driver.window_handles) > 2 :
        driver.switch_to.window(driver.window_handles[-1])
        driver.close()

        driver.switch_to.window(driver.window_handles[-1])
        driver.close()

        last_tab = driver.window_handles[-1]
        driver.switch_to.window(window_name=last_tab)
    else : 
        last_tab = driver.window_handles[-1]
        driver.switch_to.window(window_name=last_tab)

def collectJobInfo():
    #with  MongoClient("mongodb://172.17.0.3:27017") as my_client: #for linux
    header = {'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.75 Safari/537.36'}
    company_url='http://www.work.go.kr/empInfo/totBusiInfo/busiSearchDetailPop.do?busino='
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
    '''.replace('        ','')
    d_path = '../web_config/driver/chromedriver_linux'
    print("start reading!")


    with  MongoClient("mongodb://127.0.0.1:27017") as my_client: #for goorm_io     
        # Create your views here.
        driver = webdriver.Chrome(d_path)
        driver.implicitly_wait(20) # 암묵적으로 웹 자원을 (최대) 20초 기다리기
        
        # worknet 로그인 및 새창 닫기
        driver.get(url='https://www.work.go.kr/seekWantedMain.do')
        login('whrnrgusdlek','dhfl108!',driver)        
     
        close_tab(driver)
        # 상세 검색 첫페이지로 이동 
        driver.get(url=(url.format(str(1))))

        # 페이지 정보 얻어오기 
        pageNo = driver.find_elements_by_css_selector('#mForm > div.nav_wrp > div')[0].text[2:-5]
        # 페이지 수만큼 반복 실행
        for i in range(1,len(pageNo)+1):
            
            # 데이터 수집시작
            tr_table = driver.find_elements_by_css_selector("#mForm > div.table-wrap > table > tbody > tr")
            for tr in tr_table :
                #새창으로 이동하기 위한 링크클릭
                #time.sleep(3)
                company_tag = tr.find_element_by_css_selector('td:nth-child(2) > a') 
                title_link = tr.find_element_by_css_selector('td:nth-child(3) > div > div > a')

                company = company_tag.text
                title = title_link.text
                work = tr.find_element_by_css_selector('td:nth-child(3) > div > p').text     

                title_link.click()
                #time.sleep(2)
                close_tab(driver)       
                address = get_data(driver)                                                                            
               
                driver.close()   
                first_tab = driver.window_handles[0]
                driver.switch_to.window(window_name=first_tab )
                # 새로 열렸던 창을 닫고 기존의 검색창으로 복귀                                 
                print({'company':company,'address':address,'title':title,'work':work})
                my_client.Jobinfo.Joblist.insert_one({'company':company,'address':address,'title':title,'work':work})

            driver.get(url=(url.format(str(i+1))))


        time.sleep(2)
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