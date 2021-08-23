from ccos.automation import check_ccos_status
from zalo_base.services import ZaloService

def check_system_status():
    print("====== SCHEDULER IS RUNNING ======")
    is_alive = check_ccos_status()
    if not is_alive:
        user_id = '895596865423073839'
        message = """Server CCOS đã tắt, vui lòng bật truy cập lại và bật thủ công:
https://apizalo-cskh.vnptbinhphuoc.vn/ccos"""
        ZaloService().send_message(user_id, message)