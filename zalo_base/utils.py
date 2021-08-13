import json

def store_json(file_name, data):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def read_json(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)

def parse_phone(phone):
    if phone and isinstance(phone, int):
        phone = str(phone)
    # if '84' in phone and phone[:2] == '84':
    phone = phone[-9:]
    return phone

def generate_qrcode(qr_code):
    qr_code = qr_code.replace(' ', '%20')
    return f"https://chart.googleapis.com/chart?cht=qr&chs=350x350&chl={qr_code}&chld=H"