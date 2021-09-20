from ccos.automation import check_ccos_status, closeDriverInstance, forceDelTempFolder
from zalo_base.services import ZaloService

def check_system_status():
    print("====== SCHEDULER IS RUNNING ======")
    is_alive = check_ccos_status()
    if not is_alive:
        manager_user_id = '4691711065705321136'
        message = """Server CCOS đã tắt, vui lòng bật truy cập lại và bật thủ công:
https://apizalo-cskh.vnptbinhphuoc.vn/ccos"""
        ZaloService().send_message(manager_user_id, message)

def free_system_storage():
    closeDriverInstance()
    forceDelTempFolder()
    