from collections import Counter
import inspect
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoAlertPresentException, UnexpectedAlertPresentException, WebDriverException
import re
import time
import pyperclip
import pandas as pd
import os

# >> test module << 

URL = 'http://qt2-kic.smartdesk.lge.com/admin/main.lge?serverType=QA2'
CPURL = 'http://qt2-kic.smartdesk.lge.com/admin/master/ordering/ordering/retrieveAppOrderingList.lge?serverType=QA2'
Verify_Dataframe = pd.DataFrame([], columns=['index', 'Context Name', 'Context ID', 'Alert Text'])

# >> QA2 server is only available 
# >> Appid is different between QA2 and Prod.

# for scale, youtube id is different from TV
cautionCP4smnt = {
    'YoutubeTV' : 95384,
    'Youtubesmnt' : 357640,
}

def ClickEvent(contribute, path) :
    driver.find_element(contribute, path).click()
    
def SendKeyEvent(contribute, path) : 
    driver.find_element(contribute, path).send_keys(Keys.CONTROL, 'v')
    
def getBaseOrderingdata() :
    base_dataframe = pd.read_csv(r'ordering_auto\ordering_test\W23L_ordering_qa2.csv')
    return base_dataframe
        
def getDetailOrdering(country, plfCode) :
    # Appdf = df
    Appdf = pd.read_csv(r'ordering_auto\ordering_test\W23L_ordering_qa2.csv')
    CountryOrdering = Appdf[Appdf['Country Name'] == country][['Country Name', 'Order Type', 'App Name', 'App Id', 'Order Number']].reset_index(drop=True)
    
    if CountryOrdering.empty :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] {country}[{plfCode}] : empty')
        return False
    
    # scale Appid only for webos23 platform 
    if 'webOSTV 23' in plfCode.split('-') :
        replace_to = {cautionCP4smnt['YoutubeTV'] : cautionCP4smnt['Youtubesmnt']}
        CountryOrdering = CountryOrdering.replace(replace_to)
        print(f"{time.ctime()} [{inspect.stack()[0].function}] scale AppId {cautionCP4smnt['YoutubeTV']} -> {cautionCP4smnt['Youtubesmnt']}")
        
    print(f"{time.ctime()} [{inspect.stack()[0].function}] Show Dataframe for CP ordering")
    print(CountryOrdering)
    
    return CountryOrdering

def isAlertPresented(delay=10) :
    time.sleep(0.5)
    alertPresented = WebDriverWait(driver, delay).until(EC.alert_is_present())
    try :
        if alertPresented :
            alert = driver.switch_to.alert
            alert.accept()
            print(f'{time.ctime()} [{inspect.stack()[0].function}] Alert has been accpted successfully')
            
        else :
            print(f'{time.ctime()} [{inspect.stack()[0].function}] Alert is not presented')
        
        return True, 'Y'
    
    except NoAlertPresentException:
        print(f'{time.ctime()} [{inspect.stack()[0].function}] No alert found.')
        return True, 'Y'
    
    except Exception as err :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] Exception error happend : {err}')
        return False, alert.text
    
def getDriver():
    global driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.implicitly_wait(5)
    driver.get(URL)
    isAlertPresented()   
    
    #     alertPresented = isAlertPresented()
    #     if alertPresented :
    #         alert = driver.switch_to.alert
    #         alert.accept()
    #         print(f'{time.ctime()} [{inspect.stack()[0].function}] Alert has been accpted successfully')
            
    #     else :
    #         print(f'{time.ctime()} [{inspect.stack()[0].function}] Alert is not presented')
        
    # except NoAlertPresentException:
    #     print(f'{time.ctime()} [{inspect.stack()[0].function}] No alert found.')
    
    # except Exception as err :
    #     print(f'{time.ctime()} [{inspect.stack()[0].function}] Exception error happend : {err}')
        
    return driver
        
def proceesLogin(id, pw) :
    ClickEvent(By.ID, 'USER')
    pyperclip.copy(id)
    SendKeyEvent(By.ID, 'USER')
    ClickEvent(By.ID, 'LDAPPASSWORD')
    pyperclip.copy(pw)
    SendKeyEvent(By.ID, 'LDAPPASSWORD')
    ClickEvent(By.ID, 'loginSsobtn')
    driver.implicitly_wait(5)
    
    if isLoginSuccess() :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] get ready to order CP')
        return True
    
    else :
        return False
    
def isLoginSuccess() :
    successful_url = 'http://epdev.lge.com:6381/portal/main/portalMain.do'
    check_url = driver.current_url.split(';')[0] # sessionId split 
    print(f'{time.ctime()} [{inspect.stack()[0].function}] current url : {check_url}')
    if check_url != successful_url :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] login failed. please check your id or password')
        ## should i have to get other id or password? 
        return False
    
    print(f'{time.ctime()} [{inspect.stack()[0].function}] successfully login at SDP site.')
    return True
    
def checkCondition():
    getDriver()
    if proceesLogin('seonghyeon.min', 'alstjdgus@4416') :
        driver.get(CPURL)
        return True
    
    else :
        print(f'{time.ctime()} check pre-condtion status (login, url...)' )
        
def setContribute(platformcode) :
    print(f'{time.ctime()} [{inspect.stack()[0].function}] Set Contribute for ordering ')
    
    ClickEvent(By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/button')
    
    idx = -1
    platformlength = len(driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/ul').find_elements(By.TAG_NAME, 'li'))
    cur_time = time.time()
    
    for num in range(2, platformlength+1) :
        candPlatformCode = driver.find_element(By.XPATH, f'/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/ul/li[{num}]/a/label').text
        modifyPlatformCode = candPlatformCode.split('-')[1]
        
        if platformcode == modifyPlatformCode :
            idx = num
            save_candPlatformCode = candPlatformCode 
            print(f'{time.ctime()} [{inspect.stack()[0].function}] ProductPlatform Code Found : {platformcode}[{idx}], time : {time.time() - cur_time:.2f} [sec]')
            break
        
    if idx == -1 :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] ProductPlatform Code is not existed, Quit Driver')
        return 
    
    time.sleep(1.5)
    
    ClickEvent(By.XPATH, f'/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[1]/td/span/div/ul/li[{idx}]/a/label')
    ClickEvent(By.XPATH, '/html/body/div/div/form[2]/div/div[1]/h3')
    ClickEvent( By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[3]/td[1]/select')
    # ClickEvent(driver, By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[3]/td[1]/select/option[1]') #request
    ClickEvent(By.XPATH, '/html/body/div/div/form[2]/div/fieldset/div/table/tbody/tr[3]/td[1]/select/option[2]') #draft    
    ClickEvent(By.XPATH, '/html/body/div/div/form[2]/div/div[2]/div[1]/select')
    ClickEvent(By.XPATH, '/html/body/div/div/form[2]/div/div[2]/div[1]/select/option[7]')
    
    time.sleep(1.5)
    
    return save_candPlatformCode

def get_cpHomeApp(dataframe, value) :
    cpApp_Home = dataframe[dataframe['Order Type'] == value ]
    
    cpAppHome_Lst = cpApp_Home[['App Name', 'App Id']].value.tolist()
    cpAppHome_dict = dict((name, id) for name, id in zip(cpApp_Home['App Name'], cpApp_Home['App Id']))
    
    print(f'{time.ctime()} [{inspect.stack()[0].function}] Home-CP as list : {cpAppHome_Lst}')
    print(f'{time.ctime()} [{inspect.stack()[0].function}] Home-CP as dict : {cpAppHome_dict}')

    return cpAppHome_Lst, cpAppHome_dict

def get_cpPremiumApp(dataframe, value) :
    cpApp_Premium = dataframe[dataframe['Order Type'] == value ]
    
    cpAppPremium_Lst = cpApp_Premium[['App Name', 'App Id']].value.tolist()
    cpAppPremium_dict = dict((name, id) for name, id in zip(cpApp_Premium['App Name'], cpApp_Premium['App Id']))
    
    print(f'{time.ctime()} [{inspect.stack()[0].function}] premium-CP as list : {cpAppPremium_Lst}')
    print(f'{time.ctime()} [{inspect.stack()[0].function}] premium-CP as dict : {cpAppPremium_dict}')
    
    return cpAppPremium_Lst, cpAppPremium_dict

def request_DropEvent() :
    global dropActions
    global homeCandiArea
    global homeTargetArea
    global premiumCandiArea
    global premiumTargetArea
    global homeCandidatelen
    global premiumCandidatelen
    global homeTargetlen
    global premiumTargetlen
    global preVerifyHomeApplst
    global preVerifyPremiumApplst
    
    preVerifyHomeApplst = []
    preVerifyPremiumApplst = []
    
    dropActions = ActionChains(driver)
    
    homeCandiArea = driver.find_element(By.XPATH, '//*[@id="candidate1"]')
    homeTargetArea = driver.find_element(By.XPATH, '//*[@id="target1"]')
    
    premiumCandiArea = driver.find_element(By.XPATH, '//*[@id="candidate2"]')
    premiumTargetArea = driver.find_element(By.XPATH, '//*[@id="target2"]')

    homeCandidatelen = len(homeCandiArea.find_elements(By.TAG_NAME, 'li'))
    premiumCandidatelen = len(premiumCandiArea.find_elements(By.TAG_NAME, 'li'))
    
    homeTargetlen = len(homeTargetArea.find_elements(By.TAG_NAME, 'li'))
    premiumTargetlen = len(premiumTargetArea.find_elements(By.TAG_NAME, 'li'))
    
    
    if homeTargetlen >= 1 :
        for idx in range(1, homeTargetlen+1) :
            text = driver.find_element(By.XPATH, f'//*[@id="target1"]/li[{idx}]/span[2]').text
            name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
            print(f'{time.ctime()} [{inspect.stack()[0].function}] [Launcher] App name (id) : {name} ({id})')
            preVerifyHomeApplst.append([name, int(id)])
    
    if premiumTargetlen >= 1 :
        for idx in range(1, premiumTargetlen+1) :
            text = driver.find_element(By.XPATH, f'//*[@id="target2"]/li[{idx}]/span[2]').text
            name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
            print(f'{time.ctime()} [{inspect.stack()[0].function}] [Premium] App name (id) : {name} ({id})')
            preVerifyPremiumApplst.append([name, int(id)])

    print(f'{time.ctime()} [{inspect.stack()[0].function}] success to get ready for drag & drop event')
    

def is_dragdrop_for_Home(Applst) :
    homeApplst = Applst 
    if homeApplst == preVerifyHomeApplst :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] {homeApplst} == {preVerifyHomeApplst}')
        return False
    # return True 

def is_dragdrop_for_Premium(Applst) :
    PremuiumApplst = Applst 
    if PremuiumApplst == preVerifyPremiumApplst :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] {PremuiumApplst} == {preVerifyPremiumApplst}')
        return False     
    # return True  
        
def response_DropEvent_for_Home(HomeApplst) :
    print(f'{time.ctime()} [{inspect.stack()[0].function}] check condition before start drag & drop event')
    if not is_dragdrop_for_Home(HomeApplst) :
        # don't need to drag and drop event.
        return 'N'
    return 'Y'

def response_DropEvent_for_Premium(PremiumApplst) :
    print(f'{time.ctime()} [{inspect.stack()[0].function}] check condition before start drag & drop event')
    if not is_dragdrop_for_Premium(PremiumApplst) :
        # don't need to drag and drop event.
        return 'N'
    return 'Y'

def Confirmation_Ordering_for_notEvent(count) :
    ClickEvent(By.XPATH, '//*[@id="orderingForm"]/div[2]/div[8]/div[2]/button[1]')

    for idx in range(count) :
        isAlertPresented(20)

    print(f'{time.ctime()} [{inspect.stack()[0].function}] Ordering has been confirmed')
    return True 

def reorganize_CP(appdict) :
    reorganizeCP = dict()
    
    for cp, cpId in dict(list(appdict.items())[:4]).items() :
        reorganizeCP[cp] = cpId
    
    for cp, cpId in dict(list(appdict.items())[:3:-1]).items() :
        reorganizeCP[cp] = cpId

    print(f'{time.ctime()} [{inspect.stack()[0].function}] reorganization of CP has been completed')
    print(f'{time.ctime()} [{inspect.stack()[0].function}] cp index : {reorganizeCP}')

    return reorganizeCP

def dragdrop4Home(dict4home) :
    # alert for dict
    alert4dict = dict()

    if len(dict4home) > 5 :
        object_home_dict = reorganize_CP(dict4home)
    else :
        object_home_dict = dict4home

    for cp, cpId in object_home_dict.items() :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] index : {cp}({cpId})')

        for idx in range(1, homeCandidatelen+1) :
            text = driver.find_element(By.XPATH, f'//*[@id="candidate1"]/li[{idx}]/span[2]').text
            name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]

            # should i have to check the FCK list?
            # if it's essential, get the elements of the fck list
            # maybe, the list of fck is in the element of the 'li-tag'
            if (name == cp) and (str(id) == str(cpId)) :
                dragItem = driver.find_element(By.XPATH, f'//*[@id="candidate1"]/li[{idx}]/span[2]')
                dropActions.move_to_element(dragItem).click_and_hold().move_to_element(homeTargetArea).release().perform()
                
                successFlag, alertext = isAlertPresented()
                alert4dict[cp] = alertext

                if successFlag :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] {cp}({cpId}) Dropped')
                
                else :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] {cp}({cpId}) Fail to Drop or FCK check.')
                    # 우선, FCK 가 없으면 해당 App은 무시하고 오더링을 시작한다
                    # 앱이 빠지는 이유는 업체 계약과 관련이 있기 때문
                break

    return alert4dict

def makeVerification(cpAppHome_dict, alert_dict) :
    # use Verify_Dataframe variable
    _alert_dict = alert_dict
    dropHomeApplst = []
    cp_for_df = [[k, v, 'None'] for k, v in cpAppHome_dict.items()]
    
    for idx in range(1, homeTargetlen+1) :
        text = driver.find_element(By.XPATH, f'//*[@id="target1"]/li[{idx}]/span[2]').text
        name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
        dropHomeApplst.append([idx, name, int(id), ''])

    # monitor whether if bad-alert with cp is existed. 
    appName = [key[1] for key in Counter(map(tuple, dropHomeApplst)).keys()]

    for idx in range(len(cp_for_df)) :
        _key = cp_for_df[idx][0]

        if _key not in appName :
            cp_for_df[idx][2] = _alert_dict[_key]
        
    Verify_Dataframe = pd.concat([Verify_Dataframe, pd.DataFrame(cp_for_df, columns=['Context Name', 'Context ID', 'Alert Text'])])

    return Verify_Dataframe

def proceedOrdering(platformcode) :
    if checkCondition() :
        # do ordering 
        Verifylst = []
        base_dataframe = getBaseOrderingdata()
        
        platformcode_parsing = setContribute(platformcode)
        
        Pagination_group = ''.join(list(driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/nav/ul').text)).split('\n')
        print(f'{time.ctime()} [{inspect.stack()[0].function}] {Pagination_group} has been allocated')
        
        startpageIdx = int(Pagination_group[Pagination_group.index('1')])
        
        if 'Next' in Pagination_group :
            endpageIdx = int(Pagination_group[Pagination_group.index('10')])
        
        else :
            endpageIdx = int(Pagination_group[-1]) 
            
        for page in range(startpageIdx, endpageIdx+1) :
            try :
                page_Xpath = f'/html/body/div/div/form[2]/div/nav/ul/li[{page}]/a'
            except :
                page_Xpath = f'/html/body/div/div/form[2]/div/nav/ul/li/a' # Pagination_group compose of only '1'
                
            ClickEvent(By.XPATH, page_Xpath)
            time.sleep(0.5)
            
            Trlen = len(driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/div[3]/table/tbody').find_elements(By.TAG_NAME, 'tr'))
            for num in range(Trlen, 0, -1) : 
                time.sleep(1.5)
                country = driver.find_element(By.XPATH, f'/html/body/div/div/form[2]/div/div[3]/table/tbody/tr[{num}]/td[2]').text
                print(f'{time.ctime()} [{inspect.stack()[0].function}] allocate coountry : {country}')
                
                country_cp_dataframe = getDetailOrdering(country, platformcode_parsing) 
                
                if not country_cp_dataframe :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] dataframe is empty')
                    continue
                
                # Make Verfiylst, CP list both home and premium.
                cpAppHome_Lst, cpAppHome_dict = get_cpHomeApp(country_cp_dataframe, 'HOME')
                cpAppPremium_Lst, cpAppPremium_dict = get_cpPremiumApp(country_cp_dataframe, 'PREMIUM')
                
                Homelen, Premiumlen = len(cpAppHome_Lst), len(cpAppPremium_Lst)
                
                for idx in range(Homelen) :
                    Verifylst.append([country, 'HOME', cpAppHome_Lst[idx][0], cpAppHome_Lst[idx][1]])
                
                for idx in range(Premiumlen) :
                    Verifylst.append([country, 'HOME', cpAppPremium_Lst[idx][0], cpAppPremium_Lst[idx][1]])
                
                
                print(f'{time.ctime()} [{inspect.stack()[0].function}] verify-List : {Verifylst}')
                
                # access detail url.
                ClickEvent(By.XPATH, f'/html/body/div/div/form[2]/div/div[3]/table/tbody/tr[{num}]/td[4]/a')
                
                try :
                    WebDriverWait(driver, 30).until(EC.presence_of_element_located(By.ID, 'target1')) # for page being loaded until element can be found for 30 sec.
                except :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] TimeOutException')
                    # /* need some exception..
                    driver.quit()

                request_DropEvent()
                
                #home
                if response_DropEvent_for_Home(cpAppHome_Lst) == 'Y' :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] start to drag and drop at Home Launcher')
                    alert_dict = dragdrop4Home(cpAppHome_dict)

                    # after drag & drop Event, make dataframe for verifying and leaving message
                    verification_Data = makeVerification(cpAppHome_dict, alert_dict)

                #premium
                if response_DropEvent_for_Premium(cpAppPremium_Lst) == 'Y' :
                    pass # do drag and drop
                
                if (response_DropEvent_for_Home == 'N') and (response_DropEvent_for_Premium == 'N') :
                    # alert pop-up twice
                    Confirmation_Ordering_for_notEvent(2)
                    continue
                
                else :
                    ClickEvent(By.XPATH, '//*[@id="orderingForm"]/div[2]/div[8]/div[2]/button[1]')
                    time.sleep(0.5)

                    ClickEvent(By.XPATH, '//*[@id="popup-todayChangeList"]/div/div/div[3]/button')
                    time.sleep(0.5)

                    sflag, alert_Text = isAlertPresented()

                    if sflag :
                        time.sleep(2.5)
                        driver.back()

                    else :
                        print(f'{time.ctime()} [{inspect.stack()[0].function}] {alert_Text} has been pop-out')




        print(f'{time.ctime()} [{inspect.stack()[0].function}] =================== check below =================== \n{verification_Data}')
        return verification_Data
    
    else :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] Fail to check Condition of selenium')
        driver.quit()
    
if __name__ == '__main__' :
    proceedOrdering('S23Y')