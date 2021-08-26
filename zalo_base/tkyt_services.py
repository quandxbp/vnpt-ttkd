from requests.api import request
from requests.models import Response
from .models import ZaloUser
from .tkyt_zalo_sdk import ZaloSDK

from .utils import *
from pathlib import Path
import requests

BASE_DIR = Path(__file__).resolve().parent.parent
CONSTANT_SITE = "https://kiemdich.binhphuoc.gov.vn"
CONFIG_FILE = 'tkyt_config.json'

class TKYT_Service:

    def __init__(self):
        self.site = self.get_site()
        self.z_sdk = ZaloSDK(self.get_access_token())
        self.title = "BCĐ phòng chống dịch Covid19 Bình Phước"
        self.default_qr = "https://4js.com/online_documentation/fjs-gst-2.50.02-manual-html/Images/grw_qr_code_example_width_3cm.jpg"

    def get_site(self):
        data = read_json(BASE_DIR / CONFIG_FILE)
        return data.get('site', CONSTANT_SITE)
    
    def get_access_token(self):
        data = read_json(BASE_DIR / CONFIG_FILE)
        return data.get('access_token', False)
    
    def set_site(self, site):
        data = read_json(BASE_DIR / CONFIG_FILE)
        data['site'] = site
        store_json(BASE_DIR / CONFIG_FILE, data)
        return data

    def post_message(self, user_id, message):
        return self.z_sdk.post_message(user_id, message=message)

    def post_multiple_message(self, messages):
        for m in messages:
            response = self.z_sdk.post_message(m.get('zuser_id'), message=m.get('message'))
            if not response.get('success'):
                return {
                    'success': 0,
                    "message": f"Error for user_id = {m.get('zuser_id')} and message = {m.get('message')}"
                }
        return {
            'success': 1,
            'message': "Success"
        }

    def get_user_detail_message(self, info):
        address = info.get('address', 'Chưa xác định')
        if info.get('district'):
            address = f"{address}, {info.get('district')}"
        if info.get('city'):
            address = f"{address}, {info.get('city')}"
        message = f"""Cảm ơn bạn đã cung cấp thông tin để đăng ký cấp quản lý
- Họ và tên: {info.get('name', "Chưa xác định")}
- Số điện thoại: {info.get('phone', 'Chưa xác định')}
- Địa chỉ: {address}"""         
        return message
    
    def get_delare_buttons(self, user_id):
        return [
            {
                "title": "Đăng ký tờ khai y tế dành cho người dân",
                "payload": {
                    "url": f"{self.site}/#/to-khai-y-te/0/{user_id}"
                },
                "type": "oa.open.url"
            },
            {
                "title": "Đăng ký tờ khai y tế dành cho tài xế",
                "payload": {
                    "url": f"{self.site}/#/to-khai-y-te/0/{user_id}"
                },
                "type": "oa.open.url"
            }
        ]
    
    def send_confirm_message(self, user_id, datas):
        phone = datas.get('phone', "Chưa xác định")
        name = datas.get('name', "Chưa xác định")
        qr_image = datas.get('qr_image', self.default_qr)

        text = f"""Cảm ơn bạn {name} - {phone} đã khai báo tờ khai Online.
Đây là mã QR Code thông tin đăng ký của bạn.
Hãy đưa thông báo này cho cán bộ tại chốt kiểm soát để xác nhận lại đăng ký."""

        return self.z_sdk.send_attachment_message(user_id, text=text, url=qr_image,)

    def send_confirm_location_message(self, user_id, datas):
        is_checkin = datas['checkin']
        longitude = datas['longitude']
        latitude = datas['latitude']
        location = f"https://www.google.com/maps?q={latitude},{longitude}&z=14&t=m&mapclient=embed"
        
        response = self.send_location_to_tkyt(user_id, location, is_checkin)
        
        message = f"""Cảm ơn đã chia sẻ vị trí hiện tại của bạn.
- Vị trí xác định: {location}"""
        return self.z_sdk.post_message(user_id, message=message)
    
    def send_confirm_at_checkpoint(self, phone):
        is_existed = ZaloUser.objects.filter(phone=phone).exists()
        if is_existed:
            user = ZaloUser.objects.get(phone=phone)
            text = f"""Thành công xác nhận thông tin tại chốt kiểm soát.
Hãy nhấn vào nút bên dưới khi đã đến địa điểm của bạn!"""
            title = "Xác nhận khi vừa tới điểm đến"
            url = "https://google.com.vn"
            kwargs = {
                'text': text,
                'title': title,
                'url': url
            }
            return self.z_sdk.post_button_message(user.user_id, **kwargs)
        else:
            return {
                'success': 0,
                'message': f'Not found user by phone number: {phone}'
            }

    def send_checker_confirm(self, user_id, message):
        buttons = [
            {
                "title": "Từ chối",
                "payload": {
                    "url": 'https://developers.zalo.me/'
                },
                "type": "oa.open.url"
            },
            {
                "title": "Xác nhận",
                "payload": {
                    "url": "https://developers.zalo.me/"
                },
                "type": "oa.open.url"
            },
        ]
        message = """Bùi Trần Đông Quân - 0981613096"""
        return self.z_sdk.post_button_message(user_id, text=message, buttons=buttons)

    
    def action_by_event(self, event_name, datas):
        if event_name == 'follow':
            user_id = datas['follower']['id']
            text = "Hãy chọn tờ khai y tế phù hợp với bạn"
            buttons = self.get_delare_buttons(user_id)

            return self.z_sdk.post_button_message(user_id, text=text, buttons=buttons)
        
        if event_name == "user_submit_info":
            user_id = datas['sender']['id']
            info = datas.get('info')
            if info:
                #TODO: Send user_id and phone to server
                response = self.send_user_info_to_tkyt(user_id, info.get('phone'))
                message = self.get_user_detail_message(info)
            else:
                message = f"Bạn chưa cung cấp đầy đủ thông tin, vui lòng thực hiện lại"
        
            return self.z_sdk.post_message(user_id, message=message)
        
        # if event_name == "oa_send_text":
        #     user_id = datas['recipient']['id']
        #     message = datas['message']['text']
            
        #     # Đăng ký cấp quản lý
        #     if "#dkquanly" in message:
        #         title = "Đăng ký tài khoản cấp Quản lý"
        #         subtitle = "Hãy cung cấp thông tin cá nhân theo mẫu để tiến hành đăng ký cấp Quản lý"
        #         user_response = self.z_sdk.get_profile(user_id)

        #         if user_response['success']:
        #             zalo_response = user_response.get('zalo_response')
        #             shared_info = zalo_response['data'].get('shared_info')
        #             if shared_info:
        #                 res = self.send_user_info_to_tkyt(user_id, shared_info.get('phone'))
        #                 message = self.get_user_detail_message(shared_info)
        #                 return self.z_sdk.post_message(user_id, message=message)
        #         return self.z_sdk.request_user_info(user_id, title=title, subtitle=subtitle)

        if event_name == "user_send_text":
            user_id = datas['sender']['id']
            message = datas['message']['text']

            # Xác nhận điểm đến
            if "#xacnhandiemden" in message:
                title = "Xác nhận vị trí hiện tại của bạn"
                subtitle = "Cung cấp vị trí điểm đến hiện tại của bạn cho BCĐ phòng chống dịch Covid-19 tỉnh Bình Phước"
                url = f"https://vnptbp-services.herokuapp.com/location/{user_id}?checkin=1"
                return self.z_sdk.post_banner_message(user_id, title=title, subtitle=subtitle, url=url)

            # Xác nhận điểm rời
            if "#xacnhandiemroi" in message:
                title = "Xác nhận vị trí hiện tại của bạn"
                subtitle = "Cung cấp vị trí hiện tại của bạn cho BCĐ phòng chống dịch Covid-19 tỉnh Bình Phước"
                url = f"https://vnptbp-services.herokuapp.com/location/{user_id}?checkin=0"
                return self.z_sdk.post_banner_message(user_id, title=title, subtitle=subtitle, url=url)

            # Khai báo Online
            if "#khaibaoonline" in message:
                text = "Hãy chọn tờ khai y tế phù hợp với bạn"
                buttons = self.get_delare_buttons(user_id)
                return self.z_sdk.post_button_message(user_id, text=text, buttons=buttons)

            # Khai báo sức khỏe
            if "#khaibaosuckhoe" in message:
                title = "Khai báo sức khỏe hằng ngày"
                subtitle = "Cung cấp thông tin sức khỏe của bạn cho BCĐ phòng chống dịch Covid-19 tỉnh Bình Phước"
                url = f"https://kiemdich.binhphuoc.gov.vn/#/theo-doi-suc-khoe/khai-bao/{user_id}"
                image_url = "https://i.imgur.com/TVVyxKY.png"
                return self.z_sdk.post_banner_message(user_id, title=title, subtitle=subtitle, image_url=image_url, url=url)
            
            if "#dangkyquanly" in message:
                title = "Đăng ký tài khoản cấp Quản lý"
                subtitle = "Hãy cung cấp thông tin cá nhân theo mẫu để tiến hành đăng ký cấp Quản lý"
                return self.z_sdk.post_message(user_id, message=message)
                user_response = self.z_sdk.get_profile(user_id)

                if user_response['success']:
                    zalo_response = user_response.get('zalo_response')
                    shared_info = zalo_response['data'].get('shared_info')
                    if shared_info:
                        res = self.send_user_info_to_tkyt(user_id, shared_info.get('phone'))
                        message = self.get_user_detail_message(shared_info)
                        return self.z_sdk.post_message(user_id, message=message)
                return self.z_sdk.request_user_info(user_id, title=title, subtitle=subtitle)

    def send_location_to_tkyt(self, user_id, location, is_checkin):
        submit_url = 'https://api.binhphuoc.gov.vn/api/xac-nhan-thong-tin/xac-nhan-checkin-checkout'
        headers = {
            'Content-Type': 'application/json'
        }
        body = {
            'zalo_user_id': user_id,
            'vi_tri': location,
            'is_checkin': is_checkin
        }
        print(f"INFO : {submit_url} \n - DATA: {body} ")

        response = requests.post(submit_url, json=body, headers=headers)
        if response.ok:
            json_res = response.json()
            print(f"INFO : {json_res.get('message', '')} ")
            return {
                'message': json_res.get('message', ''),
                'success': 1
            }
        else:
            print(f"ERROR : {submit_url} \n {response.text}" )
            return {
                'message': response.text,
                'success': 0
            }
    
    def send_user_info_to_tkyt(self, user_id, phone):
        def parse_phone(phone):
            if phone and isinstance(phone, int):
                phone = str(phone)
            if '84' in phone and phone[:2] == '84':
                phone = phone[-9:]
            return phone
        
        phone = parse_phone(phone)
        # if phone and '84' in phone 
        submit_url = 'https://api.binhphuoc.gov.vn/api/van-tai/dang-ky-quan-ly-zalo'
        headers = {
            'Content-Type': 'application/json',
            'Authorization': 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IjIiLCJuYmYiOjE2Mjc0Mzk2NzMsImV4cCI6MTYyODA0NDQ3MywiaWF0IjoxNjI3NDM5NjczfQ.ZFAVBoOf7MdDRMtYqUQvb_Hy1JKIpWHsouGXepCcYHw'
        }
        body = {
            'zalo_user_id': user_id,
            'so_dien_thoai': phone,
        }
        print(f"INFO : {submit_url} \n - DATA: {body} ")
        response = requests.post(submit_url, json=body, headers=headers)
        if response.ok:
            json_res = response.json()
            print(f"INFO : {json_res.get('message', '')} ")
            return {
                'message': json_res.get('message', ''),
                'success': 1
            }
        else:
            print(f"ERROR : {submit_url} \n {response.text}" )
            return {
                'message': response.text,
                'success': 0
            }


        
