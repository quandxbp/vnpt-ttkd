from requests.api import request
from requests.models import Response
from .models import ZaloUser
from .zalo_sdk import ZaloSDK
from .vnpt_service import VnptService

from oracle_db.oracle_service import ORACLE_SERVICE
from ccos.services import regist_phone
from django.contrib.staticfiles.storage import staticfiles_storage
from django.conf import settings

from .utils import *
from pathlib import Path
import requests
import datetime

BASE_DIR = Path(__file__).resolve().parent.parent

try:
    OracleService = ORACLE_SERVICE()
except Exception:
    OracleService = False


class ZaloService:

    def __init__(self):
        self.z_sdk = ZaloSDK(self.get_access_token())
        self.manager_user_id = '4691711065705321136'
        # self.manager_user_id = '6046163127961711684'
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
        return OracleService.get_client_by_user_id(user_id) if OracleService else {}
    
    def send_message(self, user_id, message):
        return self.z_sdk.post_message(user_id, message=message)

    def submit_regist_payment(self, datas):
        user_id = datas.get('user_id')
        user_phone = datas.get('user_phone')
        payment_code = datas.get('payment_code')
        is_final = datas.get('is_final')
        
        clients = OracleService.get_client_by_payment_code(user_phone, payment_code) if OracleService else []
        if len(clients) == 1 or (is_final and len(clients) >= 1):
            now = datetime.datetime.now()
            regist_code = clients[0][0]
            if not OracleService.check_existed_registed_bill(user_id, regist_code):
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

    def send_message_to_manager(self, user_info, message, phone, package):
        sender = user_info.get('name', 'Không xác định')

        now = datetime.datetime.now().strftime('%d/%m/%Y %H:%m')
        manager_message = f"""{now} - {sender} - {phone} - {package}
{message}"""
        self.z_sdk.post_message(self.manager_user_id, message=manager_message)
        
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
                if OracleService:
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
                    if OracleService:
                        OracleService.insert_zalo_user(user_id, data)
                    message = self._get_user_detail_message(info)
                    return self.z_sdk.post_message(user_id, message=message)

                if '#tracuucuoc' in message:
                    try:
                        result = VnptService().get_payment_debt(user_id)
                        if result['success']:
                            debts = result['data']
                            if len(debts) == 1:
                                data = debts[0]
                                dt = f"{int(data['thang'])}/{int(data['nam'])}"
                                name = data['ten_tt']
                                address = data['diachi_tt']
                                money = f"{data['tong_pt']:,} đ"
                                qrcode_url = generate_qrcode(data['qrcode'])
                                payment_code = data['ma_tt']
                                message = f"""VNPT thông báo cước dịch vụ tháng {dt} của khách hàng là:
• Mã thanh toán: {payment_code}
• Tên khách hàng: {name}
• Địa chỉ: {address}
• Tổng cộng tiền thanh toán: {money}
Bạn có thể quét mã trực tiếp hoặc tải về máy và sử dụng chức năng quét QR code thông qua ứng dụng VNPT Pay"""
                                text = f"QR Code với mã thanh toán {payment_code} - tổng giá trị hoá đơn {money}"
                                self.z_sdk.post_message(user_id, message=message)
                                self.z_sdk.send_attachment_message(
                                    user_id,
                                    text=text, 
                                    url=qrcode_url
                                )
                            else:
                                init_data = debts[0]
                                dt = f"{int(init_data['thang'])}/{int(init_data['nam'])}"
                                name = init_data['ten_tt']
                                address = init_data['diachi_tt']
                                message = f"""VNPT thông báo cước dịch vụ tháng {dt}, quý khách có tổng cộng {len(debts)} hoá đơn cần thanh toán:
• Tên khách hàng: {name}
• Địa chỉ: {address}
"""
                                qr_codes = []
                                for idx,data in enumerate(debts):
                                    if data and len(data):
                                        money = f"{data['tong_pt']:,} đ"
                                        qrcode_url = generate_qrcode(data['qrcode'])
                                        payment_code = data['ma_tt']
                                        qr_codes.append((qrcode_url, payment_code, money))
                                        
                                        message += f"""• Số tiền cần thanh toán thanh toán cho hoá đơn {payment_code}: {money}
"""
                                    message += "Bạn có thể quét mã trực tiếp hoặc tải về máy về sử dụng chức năng quét QR code thông qua ứng dụng VNPT Pay"
                                    self.z_sdk.post_message(user_id, message=message)
                                    for qrcode_url, payment_code, money in qr_codes:
                                        text = f"QR Code với mã thanh toán {payment_code} - tổng giá trị hoá đơn {money}"
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
                            return self.z_sdk.post_message(user_id, message=result.get('message', "Không tìm thấy dữ liệu"))
                    except Exception as err:
                        message = f"Phát sinh lỗi trong quá trình truy vấn: {err}"
                        return self.z_sdk.post_message(user_id, message=message)
                
                if '$ccos' in message:
                    splitted_data = message.split('-')

                    try:
                        phone = splitted_data[1]
                        package = splitted_data[2]

                        self.z_sdk.post_message(user_id, message="Đang tiến hành đăng ký, vui lòng đợi ...")

                        result = regist_phone(phone, package)

                        message = result.get('message', "Không đúng cú pháp đăng ký")

                        if user_id != self.manager_user_id:
                            self.send_message_to_manager(info, message, phone, package)

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
                    
                

                    
            
            

    
