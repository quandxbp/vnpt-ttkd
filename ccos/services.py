from .automation import *

def process_content(state, datas):
    try:
        if state == 'system':
            is_open = datas.get('is_open')
            if is_open:
                createDriverInstance()
            else:
                closeDriverInstance()
        if state == 'signin':
            username = datas.get('username')
            password = datas.get('password')
            signin_ccos(username, password)
        if state == 'otp':
            otp = datas.get('otp')
            send_otp(otp)
        if state == 'connection':
            return {
                'success': 1,
                'is_alive': check_connection()
            }
        return {
            'success': 1,
            'message': 'Success'
        }
    except Exception as err:
        return {
            'success': 0,
            'message': str(err)
        }

def regist_phone(phone, package):
    return regist_phone_package(phone, package)