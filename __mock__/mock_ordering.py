from collections import Counter
from itertools import chain
from selenium.webdriver.common.keys import Keys
from selenium import webdriver
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.alert import Alert
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoAlertPresentException, UnexpectedAlertPresentException, WebDriverException, TimeoutException

import re
import time
import selenium
import pyperclip
import inspect
import pandas as pd

# >> test module << 
# [fix1] windows brower resolution is optimized at {'width': 2576, 'height': 1415}
URL = 'http://qt2-kic.smartdesk.lge.com/admin/main.lge?serverType=QA2'
CPURL = 'http://qt2-kic.smartdesk.lge.com/admin/master/ordering/ordering/retrieveAppOrderingList.lge?serverType=QA2'
Verify_Dataframe = pd.DataFrame([], columns=['Country', 'Context Name', 'Context ID', 'Alert Text'])
platform_code = 'S23Y'

# >> QA2 server is only available 
# >> Appid is different between QA2 and Prod.

# for scale, youtube id is different from TV
cautionCP4smnt = {
    'YoutubeTV' : 95384,
    'Youtubesmnt' : 357640
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
        return CountryOrdering
    
    # scale Appid only for webos23 platform 
    if 'webOSTV 23' in plfCode.split('-') : 
    # if platform_code in plfCode.split('-') : 
        replace_to = {cautionCP4smnt['YoutubeTV'] : cautionCP4smnt['Youtubesmnt']}
        CountryOrdering = CountryOrdering.replace(replace_to)
        print(f"{time.ctime()} [{inspect.stack()[0].function}] scale AppId {cautionCP4smnt['YoutubeTV']} -> {cautionCP4smnt['Youtubesmnt']}")
        
    print(f"{time.ctime()} [{inspect.stack()[0].function}] Show Dataframe for CP ordering")
    print(CountryOrdering)
    
    return CountryOrdering

def isAlertPresented(delay=10) :
    time.sleep(0.5)
    try :
        alertPresented = WebDriverWait(driver, delay).until(EC.alert_is_present())
        
        if isinstance(alertPresented, selenium.webdriver.common.alert.Alert) :
            alert = driver.switch_to.alert
            alert_text = alert.text
            alert.accept()
            print(f'{time.ctime()} [{inspect.stack()[0].function}] Alert has been presented, alert text : {alert_text}')
            return True, alert_text
        else :
            print(f'{time.ctime()} [{inspect.stack()[0].function}] Alert is not presented')
            return True, 'NoAlert'

    except (NoAlertPresentException, TimeoutException):
        print(f'{time.ctime()} [{inspect.stack()[0].function}] No alert found.')
        return True, 'NoAlert'
    
    except Exception as err :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] Exception error happend : {err}')
        return False, err
    
def getDriver():
    global driver
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()))
    driver.maximize_window()
    driver.implicitly_wait(5)
    driver.get(URL)
    isAlertPresented()   
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
    
    cpAppHome_Lst = cpApp_Home[['App Name', 'App Id']].values.tolist()
    cpAppHome_dict = dict((name, id) for name, id in zip(cpApp_Home['App Name'], cpApp_Home['App Id']))
    
    print(f'{time.ctime()} [{inspect.stack()[0].function}] Home-CP as list : {cpAppHome_Lst}')
    print(f'{time.ctime()} [{inspect.stack()[0].function}] Home-CP as dict : {cpAppHome_dict}')

    return cpAppHome_Lst, cpAppHome_dict

def get_cpPremiumApp(dataframe, value) :
    cpApp_Premium = dataframe[dataframe['Order Type'] == value ]
    
    cpAppPremium_Lst = cpApp_Premium[['App Name', 'App Id']].values.tolist()
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
    if homeTargetlen >= 1 :
        for idx in range(1, homeTargetlen+1) :
            text = driver.find_element(By.XPATH, f'//*[@id="target1"]/li[{idx}]/span[2]').text
            name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
            print(f'{time.ctime()} [{inspect.stack()[0].function}] [Launcher] App name (id) : {name} ({id})')
            preVerifyHomeApplst.append([name, int(id)])
    
    premiumTargetlen = len(premiumTargetArea.find_elements(By.TAG_NAME, 'li'))
    if premiumTargetlen >= 1 : 
        for idx in range(1, premiumTargetlen+1) :
            text = driver.find_element(By.XPATH, f'//*[@id="target2"]/li[{idx}]/span[2]').text
            name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
            print(f'{time.ctime()} [{inspect.stack()[0].function}] [Premium] App name (id) : {name} ({id})')
            preVerifyPremiumApplst.append([name, int(id)])

    print(f'{time.ctime()} [{inspect.stack()[0].function}] success to get ready for drag & drop event')
    
def get_current_CP_home() :
    _home_app_lst = []
    
    homeTargetlen = len(homeTargetArea.find_elements(By.TAG_NAME, 'li'))
    
    for idx in range(1, homeTargetlen+1) :
        text = driver.find_element(By.XPATH, f'//*[@id="target1"]/li[{idx}]/span[2]').text
        name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
        _home_app_lst.append([name, int(id)])
        
    print(f'{time.ctime()} [{inspect.stack()[0].function}] orderedHomeList : {_home_app_lst}')
    
    return _home_app_lst
    
def get_current_CP_premium() :
    _premium_app_lst = []
    
    premiumTargetlen = len(premiumTargetArea.find_elements(By.TAG_NAME, 'li'))
    
    for idx in range(1, premiumTargetlen+1) :
        text = driver.find_element(By.XPATH, f'//*[@id="target2"]/li[{idx}]/span[2]').text
        name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
        _premium_app_lst.append([name, int(id)])
        
    print(f'{time.ctime()} [{inspect.stack()[0].function}] orderedPremiumList : {_premium_app_lst}')
    return _premium_app_lst

def is_dragdrop_for_Home(Applst) :
    homeApplst = Applst 
    if homeApplst == cpAppHome_Lst :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] drag & drop event do not need to be run')
        return False
    return True 

def is_dragdrop_for_Premium(Applst) :
    PremuiumApplst = Applst 
    if PremuiumApplst == cpAppPremium_Lst :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] drag & drop event do not need to be run')
        return False     
    return True  
        
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

# todayChangeListPopUp check?
def Confirmation_Ordering_for_Drop_Event(count) :
    ClickEvent(By.XPATH, '//*[@id="orderingForm"]/div[2]/div[8]/div[2]/button[1]') # click confirm
    
    _, _text = isAlertPresented(5)
    
    if _text == 'NoAlert':
        # today-changelist pop-up happen
        ClickEvent(By.XPATH, '//*[@id="popup-todayChangeList"]/div/div/div[3]/button')
        
        while(True) :
            _, _text = isAlertPresented(10) 
            ## return value
            # True, do you want to confirm ?
            # True, success confirm
            if _text == 'NoAlert' :
                _sflag = True
                print(f'{time.ctime()} [{inspect.stack()[0].function}] comfirmFlag : {_sflag}')
                break
        
    else :
        _sflag, _ = isAlertPresented(5)
    
    return _sflag

def reorganize_CP(appdict) :
    reorganizeCP = dict()
    
    for cp, cpId in dict(list(appdict.items())[:4]).items() :
        reorganizeCP[cp] = cpId
    
    for cp, cpId in dict(list(appdict.items())[:3:-1]).items() :
        reorganizeCP[cp] = cpId

    print(f'{time.ctime()} [{inspect.stack()[0].function}] reorganization completed')
    print(f'{time.ctime()} [{inspect.stack()[0].function}] cp : {reorganizeCP}')

    return reorganizeCP

def cleanTargetArea(area) :
    home_TargetAreaLen = len(homeTargetArea.find_elements(By.TAG_NAME, 'li'))
    home_TargetArea = homeCandiArea
    premium_TargetAreaLen = len(premiumTargetArea.find_elements(By.TAG_NAME, 'li'))
    premium_TargetArea = premiumCandiArea
    
    #home
    if area == 'target1':
        for idx in range(home_TargetAreaLen, 0, -1) :
            print(f'{time.ctime()} [{inspect.stack()[0].function}] clean {area}')
            dragItem = driver.find_element(By.XPATH, f'//*[@id="target1"]/li[{idx}]/span[2]')
            dropActions.move_to_element(dragItem).click_and_hold().move_to_element(home_TargetArea).release().perform()
            
            isAlertPresented(3)
    
    #premium
    else :
        if (premium_TargetAreaLen - home_TargetAreaLen) > 0 :
            for idx in range(premium_TargetAreaLen, home_TargetAreaLen, -1) :
                print(f'{time.ctime()} [{inspect.stack()[0].function}] clean {area}')
                dragItem = driver.find_element(By.XPATH, f'//*[@id="target2"]/li[{idx}]/span[2]')
                dropActions.move_to_element(dragItem).click_and_hold().move_to_element(premium_TargetArea).release().perform()

                isAlertPresented(3)
        
        else :
            print(f'{time.ctime()} [{inspect.stack()[0].function}] complete to check PremiumArea')
            return

    print(f'{time.ctime()} [{inspect.stack()[0].function}] Complete to clean area[{area}] ')

def check_plfmlist(dict_home) :
    cur_time = time.time()
    mapping_cp = [[cp, str(cpId)] for cp, cpId in dict_home.items()]
    print(f'{time.ctime()} [{inspect.stack()[0].function}] checkEnablePlatformList start')
    
    for idx in range(1, homeCandidatelen+1) :
        text = driver.find_element(By.XPATH, f'//*[@id="candidate1"]/li[{idx}]/span[2]').text
        plfmlist = driver.find_element(By.XPATH, f'//*[@id="candidate1"]/li[{idx}]').get_attribute('plfmlist')
        name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
        
        if [name, str(id)] in mapping_cp :
            print(f'{time.ctime()} [{inspect.stack()[0].function}] platformlist "{set(list(plfmlist))}"')
            if platform_code not in plfmlist :
                print(f'{time.ctime()} [{inspect.stack()[0].function}] platformlist del')
                del mapping_cp[name]
            else :
                print(f'{time.ctime()} [{inspect.stack()[0].function}] platformlist skip')
                continue

    print(f'{time.ctime()} [{inspect.stack()[0].function}] checkEnablePlatformList time : {time.time() - cur_time:.2f}[sec] ')
    print(f'{time.ctime()} [{inspect.stack()[0].function}] checkEnablePlatformList end')
    return mapping_cp

def dragdrop_Home(dict_home) :
    # alert for dict
    alert_home_dict = dict()
    respHomedict = dict(check_plfmlist(dict_home))
    
    if len(respHomedict) > 5 :
        object_home_dict = reorganize_CP(respHomedict)
    else :
        object_home_dict = respHomedict

    for cp, cpId in object_home_dict.items() :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] index : {cp}({cpId})')

        for idx in range(1, homeCandidatelen+1) :
            text = driver.find_element(By.XPATH, f'//*[@id="candidate1"]/li[{idx}]/span[2]').text
            name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]

            if (name == cp) and (str(id) == str(cpId)) :
                dragItem = driver.find_element(By.XPATH, f'//*[@id="candidate1"]/li[{idx}]/span[2]')
                dropActions.move_to_element(dragItem).click_and_hold().move_to_element(homeTargetArea).release().perform()
                
                successFlag, alertext = isAlertPresented(1)
                alert_home_dict[cp] = alertext

                if 'not available' not in alertext :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] {cp}({cpId}) Dropped')
                
                else :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] {cp}({cpId}) Fail to Drop or FCK check.')
                    # 우선, FCK 가 없으면 해당 App은 무시하고 오더링을 시작한다
                    # 앱이 빠지는 이유는 업체 계약과 관련이 있기 때문
                    
                break
            
    print(f'{time.ctime()} [{inspect.stack()[0].function}] alert4dict : {alert_home_dict}')

    return alert_home_dict

def dragdrop_Premium(dict_premium) :
    alert_premium_dict = dict()
    respPremiumdict = dict(check_plfmlist(dict_premium))
    
    for cp, cpId in respPremiumdict.items() :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] index : {cp}({cpId})')
        
        for idx in range(1, premiumCandidatelen+1) :
            text = driver.find_element(By.XPATH, f'//*[@id="candidate2"]/li[{idx}]/span[2]').text
            name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
            
            if (name == cp) and (str(id) == str(cpId)) :
                dragItem = driver.find_element(By.XPATH, f'//*[@id="candidate2"]/li[{idx}]/span[2]')
                dropActions.move_to_element(dragItem).click_and_hold().move_to_element(premiumTargetArea).release().perform()
                
                successFlag, alertext = isAlertPresented(1)
                alert_premium_dict[cp] = alertext
                
                if 'not available' not in alertext :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] {cp}({cpId}) Dropped')
                    
                else :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] {cp}({cpId}) Fail to Drop or FCK check.')
                
                break
                    
    print(f'{time.ctime()} [{inspect.stack()[0].function}] alert4dict : {alert_premium_dict}')
    
    return alert_premium_dict
    
def prepare_Verification(area, cp_dict, alert_dict, country) :
    # use Verify_Dataframe variable
    _alert_dict = alert_dict
    dropCPlst = []
    cp_for_df = [[country, k, v, 'None'] for k, v in cp_dict.items()]
    
    homeTargetlen = len(homeTargetArea.find_elements(By.TAG_NAME, 'li'))
    premiumTargetlen = len(premiumTargetArea.find_elements(By.TAG_NAME, 'li'))
    
    if area == 'target1' :
        for idx in range(1, homeTargetlen+1) :
            text = driver.find_element(By.XPATH, f'//*[@id="{area}"]/li[{idx}]/span[2]').text
            name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
            dropCPlst.append([idx, name, int(id), ''])
    
    elif area == 'target2' :
        for idx in range(homeTargetlen+1, premiumTargetlen+1) :
            text = driver.find_element(By.XPATH, f'//*[@id="{area}"]/li[{idx}]/span[2]').text
            name, id = re.sub(r' \([^)]*\)', '', text), re.compile('\(([^)]+)').findall(text)[0]
            dropCPlst.append([idx, name, int(id), ''])
    
        
    print(f'{time.ctime()} [{inspect.stack()[0].function}] drop list : {dropCPlst}, area : {area}')

    # monitor whether if bad-alert with cp is existed. 
    appName = [key[1] for key in Counter(map(tuple, dropCPlst)).keys()]

    for idx in range(len(cp_for_df)) :
        _key = cp_for_df[idx][1]

        if _key not in appName :
            cp_for_df[idx][3] = _alert_dict[_key]
        
    VerifyDataframe = pd.concat([Verify_Dataframe, pd.DataFrame(cp_for_df, columns=['Country', 'Context Name', 'Context ID', 'Alert Text'])])

    print(f'{time.ctime()} [{inspect.stack()[0].function}] complete making verification of dataframe \n{VerifyDataframe}')
    
    return VerifyDataframe 

def proceed_verification(dataframe, country, object) :
    if dataframe.empty : 
        print(f'{time.ctime()} [{inspect.stack()[0].function}] emptyDataframe')
        return False
        
    print(f'{time.ctime()} [{inspect.stack()[0].function}] request verification [country : {country}, params : {object}]')
    obj_verification = object
    parser_dataframe = dataframe[(dataframe['Country'] == country) & (dataframe['Alert Text'] == 'None')][['Context Name', 'Context ID']]
    convert_pair_data = parser_dataframe.values.tolist()
    
    drop_cp_name = [cp for cp, _ in convert_pair_data]
    original_cp_name = [cp for cp, _ in obj_verification]

    print(f'{time.ctime()} [{inspect.stack()[0].function}] lst_converted : {convert_pair_data}')
    
    # case 1 : normal verification of matching all components
    if convert_pair_data == obj_verification :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] {country} Data verification : {True}')
        return True
    
    # case 2 : CP are not oreded cause of some reasons (contract of CP, App qa Failed etc..)
    # in that case, CP would be skipped + check order except that cp.
    else :
        diff_res = list(set(original_cp_name).difference(set(drop_cp_name)))
        if not diff_res :
            print(f'{time.ctime()} [{inspect.stack()[0].function}] {country} Data verification : {True}')
            return True
        
        else : # exist some cp that are not dropped
            # check order
            drop_cp_order = dict([[cp, order] for order, cp in enumerate(drop_cp_name, 1)])
            original_cp_order = dict([[cp, order] for order, cp in enumerate(original_cp_name, 1)])
            step_order = 0
                        
            for k, v in original_cp_order.items() :
                if k in drop_cp_name :
                    if v == drop_cp_order[k] :
                        continue
                    elif v == drop_cp_order[k] + step_order :
                        continue
                    else :
                        print(f'{time.ctime()} [{inspect.stack()[0].function}] {country} Data verification : {False}')
                        return False
                else :
                    step_order += 1
                    
            print(f'{time.ctime()} [{inspect.stack()[0].function}] {country} Data verification : {True}')
            return True  
        
def set_verification_data(country) :
    _home_value = get_current_CP_home()
    _premium_value = get_current_CP_premium()
    
    for idx in range(len(_home_value)) :
        _verifyList.append([country, 'HOME', _home_value[idx][0], _home_value[idx][1]])
        
    for idx in range(len(_premium_value)) :
        _verifyList.append([country, 'PREMIUM', _premium_value[idx][0], _premium_value[idx][1]])
        
    print(f'{time.ctime()} [{inspect.stack()[0].function}] {_verifyList}')
    
        
def proceedOrdering(platformcode) :
    global cpAppHome_Lst
    global cpAppPremium_Lst
    global _verifyList
    
    _verifyList = []
    
    if checkCondition() :
        # do ordering 
        base_dataframe = getBaseOrderingdata()
        platformcode_parsing = setContribute(platformcode)
        
        Pagination_group = ''.join(list(driver.find_element(By.XPATH, '/html/body/div/div/form[2]/div/nav/ul').text)).split('\n')
        print(f'{time.ctime()} [{inspect.stack()[0].function}] {Pagination_group} page has been allocated')
        
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
                
                if country_cp_dataframe.empty :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] dataframe is empty')
                    continue
                
                # Make Verfiylst, CP list both home and premium.
                cpAppHome_Lst, cpAppHome_dict = get_cpHomeApp(country_cp_dataframe, 'HOME')
                cpAppPremium_Lst, cpAppPremium_dict = get_cpPremiumApp(country_cp_dataframe, 'PREMIUM')
                
                Homelen, Premiumlen = len(cpAppHome_Lst), len(cpAppPremium_Lst)
                        
                # for idx in range(Homelen) :
                #     Verifylst.append([country, 'HOME', cpAppHome_Lst[idx][0], cpAppHome_Lst[idx][1]])
                
                # for idx in range(Premiumlen) :
                #     Verifylst.append([country, 'PREMIUM', cpAppPremium_Lst[idx][0], cpAppPremium_Lst[idx][1]])
                
                # print(f'{time.ctime()} [{inspect.stack()[0].function}] verify-List : {Verifylst}')

                # access detail url.
                currWindow = driver.current_url
                ClickEvent(By.XPATH, f'/html/body/div/div/form[2]/div/div[3]/table/tbody/tr[{num}]/td[4]/a')
                curr_time = time.time()
                # WebDriverWait(driver, 30).until(EC.presence_of_element_located(By.ID, 'target1')) # for page being loaded until element can be found for 30 sec.
                while driver.current_url == currWindow :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] Page Loading until element can be found ')
                print(f'{time.ctime()} [{inspect.stack()[0].function}] take {time.time() - curr_time:.2f} [sec] to get Page')
            
                request_DropEvent()
                
                #home
                check_homelst = get_current_CP_home()
                respHome = response_DropEvent_for_Home(check_homelst) # return 'Y' or 'N'
                if respHome == 'Y' :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] start DragandDrop Event area : home')
                    cur_time = time.time()
                    # first, Clean CPs Target area
                    homeTargetlen = len(homeTargetArea.find_elements(By.TAG_NAME, 'li'))
                    if homeTargetlen >= 1 :
                        cleanTargetArea('target1')
                    
                    alert_home_dict = dragdrop_Home(cpAppHome_dict)

                    # after drag & drop Event, make dataframe for verifying and leaving message
                    verification_Data = prepare_Verification('target1', cpAppHome_dict, alert_home_dict, country)
                    
                    resp = proceed_verification(verification_Data, country, cpAppHome_Lst)
                    
                    if not resp :
                        print(f'{time.ctime()} [{inspect.stack()[0].function}] [Home] Order of CP [{country}] are wrong. other country is going to be proceeded')
                        driver.back()
                        continue
                    
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] {country} of ordering time : {time.time() - cur_time:.2f}[sec]')

                #premium
                check_premiumlst = get_current_CP_premium()
                respPremium = response_DropEvent_for_Premium(check_premiumlst) # return 'Y' or 'N'
                if respPremium == 'Y' :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] start DragandDrop Event area : Premium')
                    cur_time = time.time()
                    
                    cleanTargetArea('target2')
                    
                    cpAppPremium_for_event = dict([[cp, cpid] for cp, cpid in cpAppPremium_dict.items() if (cp, cpid) not in cpAppHome_dict.items()])
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] cp list for event : {cpAppPremium_for_event}')
                    
                    alert_premium_dict = dragdrop_Premium(cpAppPremium_for_event)
                    
                    verification_Data = prepare_Verification('target2', cpAppPremium_for_event, alert_premium_dict, country)
                    
                    cpAppPremium_for_event_lst = [[cp, cpid] for cp, cpid in cpAppPremium_for_event.items()]
                    resp = proceed_verification(verification_Data, country, cpAppPremium_for_event_lst)
                    
                    if not resp : # Verificiation of Data has been failed,
                        print(f'{time.ctime()} [{inspect.stack()[0].function}] [Premium] Order of CP [{country}] are wrong. other country is going to be proceeded')
                        driver.back()
                        continue
                
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] {country} of ordering time : {time.time() - cur_time:.2f}[sec]')


                # make data for verifying
                set_verification_data(country)
                

                # confirmation step 
                if (respHome == 'N') and (respPremium == 'N') :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] [1] orderingConfirm start')
                    sucess_flag = Confirmation_Ordering_for_Drop_Event(2)

                else :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] [2] orderingConfirm start')
                    ClickEvent(By.XPATH, '//*[@id="orderingForm"]/div[2]/div[8]/div[2]/button[1]') # Click confirm

                    try :
                        ClickEvent(By.XPATH, '//*[@id="popup-todayChangeList"]/div/div/div[3]/button') # todayChangePopup confirm
                    except :
                        sucess_flag, _ = isAlertPresented(1.5) # do you want to confirm? -> yes
                    else :  
                        sucess_flag, _ = isAlertPresented(1.5) # do you want to confirm? -> yes
                        isAlertPresented(20) # sucess to confirm?
                        
                    time.sleep(0.5)
                    
                if sucess_flag :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] OrderingConfirm : {True}')
                    time.sleep(1.5)
                else :
                    print(f'{time.ctime()} [{inspect.stack()[0].function}] OrderingConfirm : {False}')

                    driver.back()

        print(f'{time.ctime()} [{inspect.stack()[0].function}] =================== check below =================== \n{_verifyList}')
        return _verifyList
    
    else :
        print(f'{time.ctime()} [{inspect.stack()[0].function}] Fail to check Condition of selenium')
        driver.quit()
    
if __name__ == '__main__' :
    proceedOrdering(platform_code)
