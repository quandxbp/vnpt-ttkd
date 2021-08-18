from seleniumwire import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import Select, WebDriverWait
from selenium.webdriver.common.alert import Alert
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException   

from multiprocessing import Process
from webdriver_manager import driver

from webdriver_manager.chrome import ChromeDriverManager

from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

# Admin@123456
from utils import store_json, read_json
import time

AVAILABLE_PACKAGES = ['VD149', 'D60G']
WEB_URL = 'http://outboundccos.vnpt.vn/Views/KhachHang/HoTroDangKY_KMCB_TT.aspx'

# Create your tests here.
def regist_phone_package(phone, package):
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument('--user-agent="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.131 Safari/537.36"')
    
    driver = webdriver.Chrome(executable_path=f"{str(BASE_DIR)}/chromedriver", options=chrome_options)

    driver.get(WEB_URL)
    new_window = f'window.open("{WEB_URL}"); '
    driver.delete_all_cookies()  
    driver.add_cookie({'name': 'ASP.NET_SessionId', 'value': 'w4l44x0gk5lx3q2d4q3vwv1v'})  # Open with cookie

    driver.execute_script(new_window)

    window_after = driver.window_handles[1]

    driver.switch_to_window(window_after)
    time.sleep(1)

    if 'HoTroDangKY_KMCB_TT' not in driver.current_url:
        driver.get(WEB_URL)
        time.sleep(3)
        if 'HoTroDangKY_KMCB_TT' not in driver.current_url:
            return {
                'success': 0,
                'message': "Lỗi hệ thống"
            }
    
    if package not in AVAILABLE_PACKAGES:
        return {
            'success': 0,
            'message': f"""Gói {package} hiện tại không được hỗ trợ"""
        }
    
    search_phone_input = driver.find_element_by_id("Content_txtSearchSTB")
    search_phone_btn = driver.find_element_by_id("Content_btnSearch")

    # Search phone input 
    search_phone_input.clear()
    search_phone_input.send_keys(phone)
    search_phone_btn.click()
    time.sleep(3)

    T1_value = driver.find_element_by_id("txtT1").get_attribute('value') or 0.0
    T2_value = driver.find_element_by_id("txtT2").get_attribute('value') or 0.0
    T3_value = driver.find_element_by_id("txtT2").get_attribute('value') or 0.0

    total = float(T1_value) + float(T2_value) + float(T3_value)

    if package == 'VD149' and total < 120000:
        return {
            'success': 0,
            'message': f"""Thuê báo có tổng tiêu dùng TKC 3 tháng gần nhất nhỏ hơn 120.000 đ. Tháng T-1: {T1_value}đ; Tháng T-2: {T2_value} đ; Tháng T-2: {T3_value} đ"""
        }
    elif package == 'D60G' and total < 100000:
        return {
            'success': 0,
            'message': f"""Thuê báo có tổng tiêu dùng TKC 3 tháng gần nhất nhỏ hơn 100.000 đ. Tháng T-1: {T1_value}đ; Tháng T-2: {T2_value} đ; Tháng T-2: {T3_value} đ"""
        }

    package_selection = Select(driver.find_element_by_id('ddlKMCB'))
    package_selection.select_by_value(package)
    submit_package_btn = driver.find_element_by_id("Content_btnKMCB")
    submit_package_btn.click()
    
    time.sleep(3)
    alert = Alert(driver)
    alert.accept()
    time.sleep(3)

    if len(driver.find_elements_by_id('Content_lblError')) > 0:
        errorContent = driver.find_element_by_id('Content_lblError').text
        return {
            'success': 0,
            'message': errorContent
        }
    time.sleep(5)
    return {
        'success': 1,
        'message': "Đăng ký thành công"
    }
    # get_attribute('value')
    # VD-149 < 120k ( TB 3 m)
    # D60 < 100k ( TB 3 m)

import os
import sys

if sys.platform.startswith("darwin"):
    CHROME_PATH = f"{str(BASE_DIR)}/chromedriver"
elif sys.platform.startswith("win32"):
    CHROME_PATH = f"{str(BASE_DIR)}/chromedriver.exe"

def createDriverInstance():
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument("--headless")
    driver = webdriver.Chrome(executable_path=CHROME_PATH, options=chrome_options)
    driver.get(WEB_URL)
    
    for request in driver.requests:
        print(request.headers.get('Cookie'))

