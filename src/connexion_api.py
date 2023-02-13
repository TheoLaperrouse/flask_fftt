import hmac
import hashlib
import random
import time
import string
import requests
import xmltodict
from dotenv import dotenv_values

config = dotenv_values(".env")


def sign_hmac_sha1(key, time_str):
    '''Sign with sha1'''
    hmac_object = hmac.new(key.encode(
        'utf-8'), time_str.encode('utf-8'), hashlib.sha1)
    return hmac_object.hexdigest()


def connexion_api(api, params=None):
    '''Connect to the FFTT database'''
    id_fftt = config['ID_FFTT']
    key = hashlib.md5(config['KEY_FFTT'].encode('utf-8')).hexdigest()
    serie = ''.join(random.choices(
        string.ascii_letters + string.digits, k=15)).upper()
    timestamp = round(time.time() * 1000)
    tmc = sign_hmac_sha1(key, str(time))
    url = f"http://www.fftt.com/mobile/pxml/{api}.php" \
        f"?serie={serie}&tm={timestamp}&tmc={tmc}&id={id_fftt}"
    if params is not None:
        url = f"{url}&{params}"
    try:
        response = requests.get(url)
        return xmltodict.parse(response.text)['liste']
    except requests.exceptions.RequestException as error:
        print(error)
        return None