import requests
from .utils import *

from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent.parent


class VnptService:

    def __init__(self):
        self.root_path = "http://192.168.110.66:8086"
        self.headers = self.get_headers()

    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.get_access_token_from_file()}'
        }

    def get_access_token_from_file(self):
        data = read_json(BASE_DIR / 'config.json')
        return data.get('vnpt_access_token', False)\
    
    def set_access_token_from_file(self, access_token):
        data = read_json(BASE_DIR / 'config.json')
        data['vnpt_access_token'] = access_token
        store_json(BASE_DIR / 'config.json', data)

    def get_access_token(self):
        url = 'http://192.168.110.66:8086/api/nguoi-dung/login?username=admin&password=admin'
        response = requests.post(url)
        if response.status_code == 200:
            json_res = response.json()
            if json_res.get('success') and json_res.get('data'):
                return self.set_access_token_from_file(json_res['data']['token'])

    def get_payment_debt(self, zalo_id):
        url = f'{self.root_path}/api/zalo-oa/tra-cuu-thong-tin-no'
        params = {
            'zalo_id': zalo_id
        }
        response = requests.get(url, params=params, headers=self.headers)
        message = "Không tìm thấy dữ liệu"
        if response.status_code == 200:
            json_res = response.json()
            if json_res.get('success') and json_res.get('data') and len(json_res['data']):
                return {
                    'success': 1,
                    'data': json_res['data']
                }
            else:
                return {
                    'success': 0,
                    'message': message
                }
        elif response.status_code == 401:
            self.get_access_token()
            return self.get_payment_debt(zalo_id)
        return {
            'success': 0,
            'message': message
        }
