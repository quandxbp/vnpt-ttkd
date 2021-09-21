import requests

class VnptService:

    def __init__(self):
        self.root_path = "http://192.168.110.66:8086"
        self.access_token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1bmlxdWVfbmFtZSI6IjEyMzQiLCJuYmYiOjE2MzIxMTk5MjksImV4cCI6MTYzMjcyNDcyOSwiaWF0IjoxNjMyMTE5OTI5fQ.2xEJGOCMUANxLo5nKDrtSQW1v8QLtEuKDHGR3a85A4Q"
        self.headers = self.get_headers()


    def get_headers(self):
        return {
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.access_token}'
        }

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
        return {
            'success': 0,
            'message': message
        }