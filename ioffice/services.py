from typing import Iterable 

import requests
from .utils import *

import sys

from pathlib import Path
from datetime import datetime


BASE_DIR = Path(__file__).resolve().parent.parent

class IofficeService():

    def __init__(self):
        self.access_token = self.get_access_token()

    def get_access_token(self):
        data = read_json(BASE_DIR / 'ioffice/data/config.json')
        return data.get('access_token', False)
    
    def set_access_token(self, access_token):
        data = read_json(BASE_DIR / 'ioffice/data/config.json')
        data['access_token'] = access_token
        store_json(BASE_DIR / 'ioffice/data/config.json', data)

    def get_units(self, offset=0, limit=50, search_query=False):
        data = read_json(BASE_DIR / 'ioffice/data/units.json')
        if search_query:
            search_query = no_accent_vietnamese(search_query.lower())
            data = list(filter(lambda x: search_query in x['raw_name'], data))
        return data[offset:limit] if limit else data

    def set_units(self, data):
        store_json(BASE_DIR / 'ioffice/data/units.json', data)

    def get_general_information(self):
        return read_json(BASE_DIR / 'ioffice/data/information.json')
    
    def set_general_information(self):
        units = self.get_units(limit=0)

        from_date = datetime(datetime.now().year, 1, 1, 0, 0, 0).strftime('%d/%m/%Y')
        end_date = datetime.now().strftime('%d/%m/%Y')
        
        total_documents, batch = 0, 100
        count = int(len(units) / 100)
        for x in range(count+1):
            start = x * batch
            end = (x+1) * batch if (x+1) * batch < len(units) else len(units)
            unit_ids = ', '.join([x['ma'] for x in units[start:end]])
            documents = self.request_documents(from_date, end_date, unit_ids)
            total_documents += sum([int(y['tong_so_di']) + int(y['tong_so_den']) for y in documents])

        data = {
            'documents': total_documents,
            'units': len(units),
            'write_date': datetime.now().strftime('%d/%m/%Y %H:%M')
        }
        store_json(BASE_DIR / 'ioffice/data/information.json', data)

    def get_headers(self):
        return {
            "Authorization": f"Bearer {self.access_token}" 
        }

    def update_units(self):
        units = self.request_units()

        def flatten(items):
            result = []
            for item in items:
                result.append(item['data'])
                if len(item.get('childs', [])):
                    result.extend(flatten(item['childs']))
            
            return result

        flatten_units = flatten(units)
        flatten_units = sorted(flatten_units, key=lambda d: int(d['ma']))
        for x in flatten_units:
            x['raw_name'] = no_accent_vietnamese(x['ten'].lower())

        self.set_units(flatten_units)


    def request_access_token(self):
        url = "https://binhphuoc-api.vnptioffice.vn/api/can-bo/access-token"
        params = {
            'refresh_token': '16324381801202109:29:49'
        }

        response = requests.get(url, params=params)
        if response.ok:
            result = response.json()
            access_token = result.get('data', {}).get('access_token')
            self.set_access_token(access_token)


    def request_units(self, limit=0):
        if limit == 5: return []
            
        url = "https://binhphuoc-api.vnptioffice.vn/api/can-bo/ds-don-vi-tu-dv-dinh-danh"

        response = requests.get(url, headers=self.get_headers())
        data = []
        if response.ok:
            result = response.json()
            if result.get('success'):
                data = result.get('data', [])
        else:
            self.request_access_token()
            return self.request_units(limit=limit+1)
        
        return data
    
    def request_documents(self, from_date, to_date, units, limit=0):
        if limit == 5: return []
        url = "https://binhphuoc-api.vnptioffice.vn/api/bao-cao-thong-ke/bao-cao-tong-hop-van-ban"
        
        params = {
            'chuoi_ma_don_vi': units,
            'tu_ngay': from_date,
            'den_ngay': to_date
        }
        response = requests.post(url, params=params, headers=self.get_headers())
        data = []
        if response.ok:
            result = response.json()
            if result.get('success'):
                data = result.get('data', [])
        else:
            self.request_access_token()
            return self.request_documents(from_date, to_date, units, limit=limit+1)
            
        
        return data
