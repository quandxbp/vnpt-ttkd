from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent.parent

from .models import ORACLE_DB
from .utils import read_json
import datetime

class ORACLE_SERVICE:

    def __init__(self):
        self.service = ORACLE_DB(self.get_config())

    def get_config(self):
        return read_json(BASE_DIR / 'config.json')
    
    def check_existed_zalo_id(self, zuser_id):
        stmt = """SELECT COUNT(*) FROM ZALO_CUSTOMER_USERS WHERE ZALO_ID = :zuser_id"""
        return self.service.query(stmt, {'zuser_id': zuser_id})[0][0]

    def insert_zalo_user(self, rows):
        self.service.insert_multiple(
            table='ZALO_CUSTOMER_USERS',
            columns=['ZALO_ID', 'NAME', 'PHONE', 'CREATEAT'],
            rows=rows
            )