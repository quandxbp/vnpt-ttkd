from seleniumwire import webdriver as wwd
from selenium import webdriver as wd
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException        

from multiprocessing import Process
from webdriver_manager import driver

from webdriver_manager.chrome import ChromeDriverManager

import os
import sys
import time

from .utils import store_json, read_json
from pathlib import Path
from requests.exceptions import ConnectionError

# admin_bpc_vnp2 / Vnpt@123456

BASE_DIR = Path(__file__).resolve().parent.parent
WEB_URL = 'http://outboundccos.vnpt.vn/Views/KhachHang/HoTroDangKY_KMCB_TT.aspx'
AVAILABLE_PACKAGES = ['VD149', 'D60G']


if sys.platform.startswith("darwin"):
    CHROME_PATH = f"{str(BASE_DIR)}/chromedriver"
elif sys.platform.startswith("win32"):
    CHROME_PATH = f"{str(BASE_DIR)}/chromedriver.exe"

def check_connection():
    try:
        driver = getCurrentDriver()
        return True
    except Exception:
        return False

def closeDriverInstance():
    os.system('taskkill -F -IM "chrome.exe"')
    os.system('taskkill -F -IM "chromedriver.exe"')

def forceDelTempFolder():
    os.system('forfiles /P C:\Windows\Temp /M * /C "cmd /c if @isdir==TRUE rmdir /S /Q @file"')

def close_driver(driver):
    driver.close()
    driver.quit()

def store_config(driver):
    cookie = False
    for request in driver.requests:
        if isinstance(request.headers.get('Cookie'), str) and 'SessionId' in request.headers.get('Cookie'):
            cookie = request.headers.get('Cookie').split('=')[1]
            break
    datas = {
        'session_id': driver.session_id,
        'url': driver.command_executor._url,
        'cookie': cookie
    }
    store_json(BASE_DIR / 'ccos_config.json', datas)

# Called by the second process only.
def getCurrentDriver():
    infor = read_json(BASE_DIR / 'ccos_config.json')
    chrome_options = wwd.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument("--disable-infobars")
    chrome_options.add_argument("--enable-file-cookies")
    chrome_options.add_argument('--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"')
    capabilities = chrome_options.to_capabilities()
    driver = wwd.Remote(command_executor=infor['url'], desired_capabilities=capabilities)
    driver.session_id = infor['session_id']

    return driver

# The main process calls this function to create the driver instance.
def createDriverInstance():
    chrome_options = wwd.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    driver = wwd.Chrome(executable_path=CHROME_PATH, options=chrome_options)
    driver.get(WEB_URL)

    store_config(driver)

def signin_ccos(username, password):
    try:
        driver = getCurrentDriver()
        username_input = driver.find_element_by_id("txtUsername")
        pw_input = driver.find_element_by_id("txtPassword")
        submit_btn = driver.find_element_by_name("btnLogin")

        username_input.clear()
        username_input.send_keys(username)
        pw_input.clear()
        pw_input.send_keys(password)
        submit_btn.click()

        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                        'Timed out waiting for PA creation ' +
                                        'confirmation popup to appear.')

            alert = Alert(driver)
            alert_text = alert.text
            alert.accept()
            close_driver(driver)
            return {
                'success': 0,
                'message': alert_text
            }
        except TimeoutException:
            return {
                'success': 1,
                'message' : "Thành công",
            }
    except ConnectionError as e:    # This is the correct syntax
        return {
            'success': 0,
            'message' : "Lỗi kết nối, vui lòng thực tắt máy ảo và thực hiện lại thao tác",
        }
    

def send_otp(otp):
    try:
        driver = getCurrentDriver()
        
        otp_input = driver.find_element_by_id("txtOtp")
        otp_input.send_keys(otp)
        driver.find_element_by_id("btnProcess").click()
        time.sleep(4)
        
        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                        'Timed out waiting for PA creation ' +
                                        'confirmation popup to appear.')

            alert = Alert(driver)
            alert_text = alert.text
            alert.accept()
            return {
                'success': 0,
                'message': alert_text
            }
        except TimeoutException:
            return {
                'success': 1,
                'message' : "Thành công",
            }
        close_driver(driver)
        closeDriverInstance()
    except ConnectionError as e:    # This is the correct syntax
        return {
            'success': 0,
            'message' : "Lỗi kết nối, vui lòng thực tắt máy ảo và thực hiện lại thao tác",
        }

def regist_phone_package(phone, package):
    infor = read_json(BASE_DIR / 'ccos_config.json')
    chrome_options = wd.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"')
    driver = wd.Chrome(executable_path=CHROME_PATH, options=chrome_options)

    driver.get(WEB_URL)
    new_window = f'window.open("{WEB_URL}"); '
    driver.delete_all_cookies()  
    driver.add_cookie({'name': 'ASP.NET_SessionId', 'value': infor['cookie']}) 
    driver.execute_script(new_window)

    window_after = driver.window_handles[1]

    driver.switch_to_window(window_after)
    time.sleep(1)
    # ===========

    if 'HoTroDangKY_KMCB_TT' not in driver.current_url:
        driver.get(WEB_URL)
        time.sleep(3)
        if 'HoTroDangKY_KMCB_TT' not in driver.current_url:
            close_driver(driver)
            return {
                'success': 0,
                'message': f"""Không thành công: Hệ thống đang tắt!"""
            }
    package = package.upper()
    if package not in AVAILABLE_PACKAGES:
        close_driver(driver)
        return {
            'success': 0,
            'message': f"""Không thành công: Gói {package} hiện tại không được hỗ trợ"""
        }
    try:
        search_phone_input = driver.find_element_by_id("Content_txtSearchSTB")
        search_phone_btn = driver.find_element_by_id("Content_btnSearch")

        # Search phone input 
        search_phone_input.clear()
        search_phone_input.send_keys(phone)
        search_phone_btn.click()

        try:
            WebDriverWait(driver, 3).until(EC.alert_is_present(),
                                        'Timed out waiting for PA creation ' +
                                        'confirmation popup to appear.')

            alert = Alert(driver)
            alert_text = alert.text
            alert.accept()
            close_driver(driver)
            return {
                'success': 0,
                'message': alert_text
            }
        except TimeoutException:

            T1_value = driver.find_element_by_id("txtT1").get_attribute('value') or 0.0
            T2_value = driver.find_element_by_id("txtT2").get_attribute('value') or 0.0
            T3_value = driver.find_element_by_id("txtT2").get_attribute('value') or 0.0

            total = float(T1_value) + float(T2_value) + float(T3_value)

            if package == 'VD149' and total >= 120000:
                close_driver(driver)
                return {
                    'success': 0,
                    'message': f"""Không thành công: Thuê báo có tổng tiêu dùng TKC 3 tháng gần nhất lớn hơn 120.000 đ. Tháng T-1: {T1_value}đ; Tháng T-2: {T2_value} đ; Tháng T-2: {T3_value} đ"""
                }
            elif package == 'D60G' and total >= 100000:
                close_driver(driver)
                return {
                    'success': 0,
                    'message': f"""Không thành công: Thuê báo có tổng tiêu dùng TKC 3 tháng gần nhất lớn hơn 100.000 đ. Tháng T-1: {T1_value}đ; Tháng T-2: {T2_value} đ; Tháng T-2: {T3_value} đ"""
                }

            package_selection = Select(driver.find_element_by_id('ddlKMCB'))
            package_selection.select_by_value(package)
            submit_package_btn = driver.find_element_by_id("Content_btnAddDSKM_KMCB")
            submit_package_btn.click()

            time.sleep(2)
            alert = Alert(driver)
            alert.accept()
            time.sleep(2)

            # driver.find_element_by_xpath("/html/body/form/div[3]/div[3]/div/div/div[2]/div/table/tbody/tr[2]/td")

            if len(driver.find_elements_by_id('Content_lblError')) > 0:
                errorContent = driver.find_element_by_id('Content_lblError').text
                close_driver(driver)
                return {
                    'success': 0,
                    'message': errorContent
                }
            close_driver(driver)
            return {
                'success': 1,
                'message': f"Thành công: Gán gói {package} cho thuê bao {phone}"
            }
    except Exception:
        close_driver(driver)
        return {
            'success': 0,
            'message': "Không thành công: Hệ thống đang tắt!"
        }

def check_ccos_status():
    infor = read_json(BASE_DIR / 'ccos_config.json')
    chrome_options = wd.ChromeOptions()
    # chrome_options.add_argument("--headless")
    chrome_options.add_argument('--disable-gpu')
    chrome_options.add_argument('--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"')
    driver = wd.Chrome(executable_path=CHROME_PATH, options=chrome_options)

    driver.get(WEB_URL)
    new_window = f'window.open("{WEB_URL}"); '
    driver.delete_all_cookies()  
    driver.add_cookie({'name': 'ASP.NET_SessionId', 'value': infor['cookie']}) 
    driver.execute_script(new_window)

    window_after = driver.window_handles[1]

    driver.switch_to_window(window_after)
    time.sleep(1)
    # ===========
    
    is_alive = True
    try:
        element = driver.find_element_by_id("Content_txtSearchSTB")
    except Exception:
        is_alive = False

    infor['is_alive'] = is_alive
    store_json(BASE_DIR / 'ccos_config.json', infor)

    time.sleep(4)
    close_driver(driver)
    return is_alive