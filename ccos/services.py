from .automation import *

def process_content(state, datas):
    try:
        if state == 'system':
            is_open = datas.get('is_open')
            if is_open:
                createDriverInstance()
                message = "Đã mở hệ thống"
            else:
                closeDriverInstance()
                message = "Đã tắt hệ thống"
        if state == 'signin':
            username = datas.get('username')
            password = datas.get('password')
            signin_ccos(username, password)
            message = "Đã đăng nhập hệ thống"
        if state == 'otp':
            otp = datas.get('otp')
            send_otp(otp)
            message = "Đã gửi mã OTP"
        if state == 'connection':
            return check_ccos_status()
        return {
            'success': 1,
            'message': message
        }
    except Exception as err:
        return {
            'success': 0,
            'message': str(err)
        }

def regist_phone(phone, package):
    return regist_phone_package(phone, package)