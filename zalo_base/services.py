from requests.api import request
from requests.models import Response
from .models import ZaloUser
from .zalo_sdk import ZaloSDK

from oracle_db.oracle_service import ORACLE_SERVICE
from ccos.services import regist_phone
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings

from .utils import *
from pathlib import Path
import requests
import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

OracleService = ORACLE_SERVICE()


class ZaloService:

    def __init__(self):
        self.z_sdk = ZaloSDK(self.get_access_token())
        self.title = "Trung tâm kinh doanh - VNPT Bình Phước"
        self.default_qr = "https://4js.com/online_documentation/fjs-gst-2.50.02-manual-html/Images/grw_qr_code_example_width_3cm.jpg"
    
    def get_access_token(self):
        data = read_json(BASE_DIR / 'config.json')
        return data.get('zalo_access_token', False)

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
    
    def get_oracle_service(self):
        return OracleService

    def get_client_by_user_id(self, user_id):
        return OracleService.get_client_by_user_id(user_id)
    
    def send_message(self, user_id, message):
        return self.z_sdk.post_message(user_id, message=message)

    def submit_regist_payment(self, datas):
        user_id = datas.get('user_id')
        user_phone = datas.get('user_phone')
        payment_code = datas.get('payment_code')
        is_final = datas.get('is_final')
        
        clients = OracleService.get_client_by_payment_code(user_phone, payment_code)
        if len(clients) == 1 or (is_final and len(clients) >= 1):
            now = datetime.datetime.now()
            regist_code = clients[0][0]
            insert_data = [(user_id, regist_code, now ,now, 0)]
            OracleService.insert_regist_bill(user_id, insert_data)
            message = "Cảm ơn bạn đã đăng ký thông tin, bây giờ bạn có thể sử dụng các dịch vụ của VNPT trên Zalo"
            return self.z_sdk.post_message(user_id, message=message)
        elif len(clients) > 1: 
            return {
                'success': 1,
                'clients': clients,
                'message': "Đính kèm thông tin khách hàng"
            }
        else:
            return {
                'success': 0,
                'message': 'Không tìm thấy thông tin'
            }
        
        
    def action_by_event(self, event_name, datas):
        # Users follow OA 
        if event_name == 'follow':
            user_id = datas['follower']['id']
            user_info = self.z_sdk.get_user_info(user_id)
            
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

                data = [(user_id, info.get('name', 'Chưa xác định'), phone, datetime.datetime.now())]
                OracleService.insert_zalo_user(user_id, data)
                message = self._get_user_detail_message(info)
            else:
                message = f"Bạn chưa cung cấp đầy đủ thông tin, vui lòng thực hiện lại tại mục Đăng ký -> Thông tin cá nhân"
        
            return self.z_sdk.post_message(user_id, message=message)

        # Receive Text 
        if event_name == "oa_send_text":
            user_id = datas['recipient']['id']
            message = datas['message']['text']

            if '#tracuucuoc' in message:
                pass

        if event_name == "user_send_text":
            user_id = datas['sender']['id']
            message = datas['message']['text']
            info = self.z_sdk.get_user_info(user_id)
            
            if not info:
                title = "Cung cấp thông tin cá nhân"
                subtitle = "Hãy cung cấp thông tin cá nhân để có thể sử dụng các dịch vụ, tiện ích của Vinaphone trên ứng dụng Zalo"
                return self.z_sdk.request_user_info(user_id, title=title, subtitle=subtitle)
            else:
                if '#dangkythongtin' in message:
                    phone = parse_phone(info.get('phone'))
                    data = [(user_id, info.get('name', 'Chưa xác định'), phone, datetime.datetime.now())]
                    OracleService.insert_zalo_user(user_id, data)
                    message = self._get_user_detail_message(info)
                    return self.z_sdk.post_message(user_id, message=message)

                if '#tracuucuoc' in message:
                    is_existed = OracleService.get_client_regist_bill_by_user_id(user_id)
                    if is_existed:
                        debts = OracleService.get_payment_debt(user_id)
                        if debts and len(debts):
                            message = " "
                            for idx,data in enumerate(debts):
                                if data and len(data):
                                    dt = f"{data[1]}/{data[0]}"
                                    name = data[2]
                                    address = data[3]
                                    money = f'{data[4]:,} đ'
                                    qrcode_url = generate_qrcode(data[5])
                                    payment_code = data[6]

                                    message += f"""VNPT thông báo cước dịch vụ của khách hàng là:
• Mã thanh toán: {payment_code}
• Tên khách hàng: {name}
• Địa chỉ: {address}
• Hoá đơn tháng: {dt}
• Tổng cộng tiền thanh toán: {money}
Bạn có thể quét mã trực tiếp hoặc tải về máy về sử dụng chức năng quét QR code thông qua ứng dụng VNPT Pay"""
                                    text = f"QR Code với mã thanh toán {payment_code} - tổng giá trị hoá đơn {money}"
                                    self.z_sdk.post_message(user_id, message=message)
                                    self.z_sdk.send_attachment_message(
                                        user_id,
                                        text=text, 
                                        url=qrcode_url
                                    )
                            return {
                                'success': 1,
                                'message': 'Đã gửi thông tin'
                            }
                        else:
                            message = "Không thể tìm thấy thông tin tra cứu cước"
                            return self.z_sdk.post_message(user_id, message=message)
                    else:
                        message = "Bạn chưa cung cấp thông tin để tra cứu cước, vui lòng vào mục Đăng ký mã khách hàng để khai báo thêm thông tin."
                        return self.z_sdk.post_message(user_id, message=message)
                
                if '$ccos' in message:
                    splitted_data = message.split('-')

                    try:
                        phone = splitted_data[1]
                        package = splitted_data[2]

                        self.z_sdk.post_message(user_id, message="Đang tiến hành đăng ký, vui lòng đợi ...")
                        result = regist_phone(phone, package)
                        message = result.get('message', """Không đúng cú pháp đăng ký 
- Liên hệ: Quân Bùi - 0835 401 439 để hỗ trợ xử lỗi""")
                        return self.z_sdk.post_message(user_id, message=message)
                    except Exception as err:
                        message = f"""Không đúng cú pháp đăng ký hoặc có lỗi hệ thông khi thực thi
- Lỗi : {str(err)}
- Liên hệ: Quân Bùi - 0835 401 439 để thông báo lỗi."""
                        return self.z_sdk.post_message(user_id, message=message)
                     
        return {
            'success': 1,
            'message': 'Success'
        }
                    
                

                    
            
            

    
