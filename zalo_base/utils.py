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
    if '84' in phone and phone[:2] == '84':
        phone = phone[-8:]
    return phone