from requests.api import request
from requests.models import Response
from .models import ZaloUser
from .zalo_sdk import ZaloSDK

from oracle_db.oracle_service import ORACLE_SERVICE

from .utils import *
from pathlib import Path
import requests
import datetime

OracleService = ORACLE_SERVICE()

class ZaloService:

    def __init__(self):
        self.z_sdk = ZaloSDK(self.get_access_token())
        self.title = "Trung tâm kinh doanh - VNPT Bình Phước"
        self.default_qr = "https://4js.com/online_documentation/fjs-gst-2.50.02-manual-html/Images/grw_qr_code_example_width_3cm.jpg"

    def _get_user_detail_message(self, info):
        address = info.get('address', 'Chưa xác định')
        if info.get('district'):
            address = f"{address}, {info.get('district')}"
        if info.get('city'):
            address = f"{address}, {info.get('city')}"
        message = f"""Thông tin cá nhân của {info.get('name', "Chưa xác định")}
• Số điện thoại: {info.get('phone', 'Chưa xác định')}
• Địa chỉ: {address}"""         
        return message
    
    def create_zalo_user(self, user_id, info):
        new_user = ZaloUser(
            user_id=user_id,
            name=info.get('name'),
            address=info.get('address'),
            ward=info.get('ward'),
            district=info.get('district'),
            city=info.get('city'),
            phone=info.get('phone'),
        )
        new_user.save()

    def client_regist(self, message):
        try:
            search_term = message.split('_')[1]
            # return ORACLE_CONNECTION.search_client(search_term)
        except IndexError:
            return False
        
    
    def action_by_event(self, event_name, datas):
        # Users follow OA 
        if event_name == 'follow':
            user_id = datas['follower']['id']
            user_profile = self.z_sdk.get_user_profile(user_id)
            
            if user_info:
                message = self._get_user_detail_message(user_info)
                return self.z_sdk.post_message(user_id, message=message)
            else:
                title = "Cung cấp thông tin cá nhân"
                subtitle = "Hãy cung cấp thông tin cá nhân để có thể sử dụng các dịch vụ, tiện ích của Vinaphone trên ứng dụng Zalo"
                return self.z_sdk.request_user_info(user_id, title=title, subtitle=subtitle)
        
        # User submit infor event
        if event_name == "user_submit_info":
            user_id = datas['sender']['id']
            info = datas.get('info')
            if info:
                phone = parse_phone(info.get('phone'))

                data = [(user_id, info.get('name', 'Chưa xác định'), phone, datetime.datetime.now)]
                OracleService.create_zalo_user(data)
                message = self._get_user_detail_message(info)
            else:
                message = f"Bạn chưa cung cấp đầy đủ thông tin, vui lòng thực hiện lại tại mục Đăng ký -> Thông tin cá nhân"
        
            return self.z_sdk.post_message(user_id, message=message)

        # Receive Text 
        if event_name == "oa_send_text":
            user_id = datas['recipient']['id']
            message = datas['message']['text']

            # User regists information
            if '#dangkythongtin' in message:
                user_profile = self.z_sdk.get_user_profile(user_id)
            
                if user_info:
                    message = self._get_user_detail_message(user_info)
                    return self.z_sdk.post_message(user_id, message=message)
                else:
                    title = "Cung cấp thông tin cá nhân"
                    subtitle = "Hãy cung cấp thông tin cá nhân để có thể sử dụng các dịch vụ, tiện ích của Vinaphone trên ứng dụng Zalo"
                    return self.z_sdk.request_user_info(user_id, title=title, subtitle=subtitle)
            if '#KH' in message or '#kh' in message:
                pass

            if '#tracuucuoc' in message:
                pass

        if event_name == "user_send_text":
            user_id = datas['sender']['id']
            message = datas['message']['text']
            
            

    
