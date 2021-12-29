import json
import re

def store_json(file_name, data):
    with open(file_name, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4)

def read_json(file_name):
    with open(file_name, encoding="utf-8") as json_file:
        return json.load(json_file)

def store_txt(file_name, txt):
    with open(file_name, "r+") as f:
        old = f.read() # read everything in the file
        f.seek(0) # rewind
        f.write(f"{txt} </br>" + old) # write the new line before

def read_txt(file_name):
    with open(file_name, "r") as f:
        return f.read()

patterns = {
    '[àáảãạăắằẵặẳâầấậẫẩ]': 'a',
    '[đ]': 'd',
    '[èéẻẽẹêềếểễệ]': 'e',
    '[ìíỉĩị]': 'i',
    '[òóỏõọôồốổỗộơờớởỡợ]': 'o',
    '[ùúủũụưừứửữự]': 'u',
    '[ỳýỷỹỵ]': 'y'
}

def no_accent_vietnamese(text):
    """
    Convert from 'Tieng Viet co dau' thanh 'Tieng Viet khong dau'
    text: input string to be converted
    Return: string converted
    """
    output = text
    for regex, replace in patterns.items():
        output = re.sub(regex, replace, output)
        # deal with upper case
        output = re.sub(regex.upper(), replace.upper(), output)
    return output