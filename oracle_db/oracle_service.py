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
        stmt = f"""SELECT COUNT(*) FROM ZALO_CUSTOMER_USERS WHERE ZALO_ID = :zuser_id"""
        return self.service.query(stmt, {'zuser_id': zuser_id})[0][0]

    def check_existed_zalo_id_regist_bill(self, zuser_id):
        stmt = f"""SELECT COUNT(*) FROM zalo_customer_register_bill WHERE ZALO_ID = :zuser_id"""
        return self.service.query(stmt, {'zuser_id': zuser_id})[0][0]

    def check_existed_client_by_phone(self, phone):
        phone = f"%{phone}"
        stmt = """SELECT COUNT(*) FROM VKHACHHANG WHERE MA_TB LIKE :phone OR DIENTHOAI LIKE :phone OR SO_DT LIKE :phone OR SDT_LIENHE LIKE :phone"""
        return self.service.query(stmt, {'phone': phone})[0][0]

    def get_client_by_user_id(self, zuser_id):
        stmt = """SELECT PHONE FROM ZALO_CUSTOMER_USERS WHERE ZALO_ID = :zuser_id"""
        phone = self.service.query(stmt, {'zuser_id': zuser_id})[0][0]
        if phone:
            is_existed = self.check_existed_client_by_phone(phone)
            return { 
                'phone': phone,
                'is_existed': is_existed 
            }
        return {}
    
    def get_client_by_payment_code(self, phone, payment_code):
        phone = f"%{phone}"
        stmt = """
        select distinct kh.ma_tt, kh.ten_tb, kh.diachi_ld, kh.so_dt from misdata.vKhachhang kh
            where (kh.ma_tt = :payment_code or kh.ma_tb = :payment_code)
                and (kh.ma_tb LIKE :phone
                    or kh.dienthoai LIKE :phone
                    or kh.so_dt LIKE :phone
                    or kh.sdt_lienhe LIKE :phone)
"""
        return self.service.query(stmt, {'phone': phone, 'payment_code': payment_code})

    def get_client_regist_bill_by_user_id(self, zuser_id):
        stmt = """SELECT COUNT(*) FROM ZALO_CUSTOMER_REGISTER_BILL WHERE ZALO_ID = :zuser_id"""
        return self.service.query(stmt, {'zuser_id': zuser_id})[0][0]
    
    def insert_zalo_user(self, zuser_id, data):
        if not self.check_existed_zalo_id(zuser_id):
            self.service.insert_multiple(
                table='ZALO_CUSTOMER_USERS',
                columns=['ZALO_ID', 'NAME', 'PHONE', 'CREATEAT'],
                rows=data
                ) 
        return True
    
    def insert_regist_bill(self, zuser_id, data):
        self.service.insert_multiple(
            table='zalo_customer_register_bill',
            columns=['ZALO_ID', 'MA_TT', 'CREATEAT', 'UPDATEAT', 'DISABLED'],
            rows=data
            )
        return True

    def get_payment_debt(self, zuser_id):
        period_stmt = """SELECT MAX(CHUKYNO) FROM QLTN_BPC.CHUKYNO@link_bpcsxkd"""
        period = self.service.query(period_stmt, {})[0][0]
        stmt = f"""select 
            nam,
            thang,
            ten_tt, 
            diachi_tt,
            tong_pt,
            qrcode,
            ma_tt
        from bcss_bpc.hddt_{period}@link_bpcsxkd
        where ma_tt in (
            select ma_tt
            from misdata.zalo_customer_register_bill a where a.zalo_id = :zuser_id)"""
        return self.service.query(stmt, {'zuser_id': zuser_id})
            