import json

def store_json(file_name, data):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def read_json(file_name):
    with open(file_name) as json_file:
        return json.load(json_file)
