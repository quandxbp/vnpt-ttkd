from .automation import *

def process_content(state, datas):
    try:
        if state == 'system':
            is_turn_on = datas('is_turn_on')
            if is_turn_on:
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
        return {
            'success': 1,
            'message': 'Success'
        }
    except Exception as err:
        return {
            'success': 0,
            'message': str(err)
        }
