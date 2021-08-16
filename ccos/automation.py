from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from multiprocessing import Process
from webdriver_manager import driver

from webdriver_manager.chrome import ChromeDriverManager

from pathlib import Path
# Admin@123456
from .utils import store_json, read_json
import time

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent
WEB_URL = 'http://outboundccos.vnpt.vn/Views/KhachHang/HoTroDangKY_KMCB_TT.aspx'


def store_config(driver):
    datas = {
        'session_id': driver.session_id,
        'url': driver.command_executor._url
    }
    store_json(BASE_DIR / 'config.json', datas)

# The main process calls this function to create the driver instance.
def createDriverInstance():
    # http://outboundccos.vnpt.vn/Views/KhachHang/HoTroDangKY_KMCB_TT.aspx
    options = Options()
    options.add_argument('--disable-infobars')
    # driver = webdriver.Chrome(executable_path=ChromeDriverManager("84.0.4147.30").install(), chrome_options=options, port=9515)
    driver = webdriver.Chrome(executable_path=ChromeDriverManager().install(), chrome_options=options, port=9515)
    driver.get(WEB_URL)
    
    store_config(driver)
    return {
        'success': 1, 
        'message': f"Success"
    }

# Called by the second process only.
def getCurrentDriver():
    infor = read_json(BASE_DIR / 'config.json')
    options = Options()
    options.add_argument("--disable-infobars")
    options.add_argument("--enable-file-cookies")
    capabilities = options.to_capabilities()
    driver = webdriver.Remote(command_executor=infor['url'], desired_capabilities=capabilities)
    driver.close()
    driver.session_id = infor['session_id']

    return driver

def otp_code(datas):
    if not datas.get('otp'):
        return {
            'success': 0, 
            'message': f"Please provide OTP"
        }
    driver = getCurrentDriver()

    otp_input = driver.find_element_by_id("txtOtp")
    otp_input.send_keys(datas.get('otp'))
    driver.find_element_by_id("btnProcess").click()

    # VD-149 < 120k ( TB 3 m)
    # D60 < 100k ( TB 3 m)
    return {
        'success': 1, 
        'message': f"Success"
    }

def signin_ccos(datas):
    if not datas.get('username') or not datas.get('password'):
        return {
            'success': 0, 
            'message': f"Please provide username and password"
        }
    driver = getCurrentDriver()

    username_input = driver.find_element_by_id("txtUsername")
    pw_input = driver.find_element_by_id("txtPassword")
    submit_btn = driver.find_element_by_name("btnLogin")

    username_input.clear()
    username_input.send_keys(datas.get('username'))
    pw_input.clear()
    pw_input.send_keys(datas.get('password'))
    submit_btn.click()
    
    return {
        'success': 1, 
        'message': f"Success"
    }

def close_ccos():
    driver = getCurrentDriver()
    driver.quit()
    return {
        'success': 1, 
        'message': f"Success"
    }

def regist_phone_package(phone, package):
    driver = getCurrentDriver()
    if 'HoTroDangKY_KMCB_TT' not in driver.current_url:
        driver.get(WEB_URL)
        time.sleep(3)
        if 'HoTroDangKY_KMCB_TT' not in driver.current_url:
            return False

    search_phone_input = driver.find_element_by_id("Content_txtSearchSTB")
    search_phone_btn = driver.find_element_by_id("Content_btnSearch")

    # Search phone input 
    search_phone_input.clear()
    search_phone_input.send_keys(phone)
    search_phone_btn.click()
    time.sleep(3)

    


