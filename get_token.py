import requests
import os
from dotenv import load_dotenv

load_dotenv()

BASE_URL = "https://openapivts.koreainvestment.com:29443"
APPKEY = os.environ["APPKEY"]
APPSECRET = os.environ["APPSECRET"]

url = f"{BASE_URL}/oauth2/tokenP"
headers = {
    "Content-Type": "application/json"
}
body = {
    "grant_type": "client_credentials",
    "appkey": APPKEY,
    "appsecret": APPSECRET
}
# access token 값은 하루 동안만 사용 가능함
# 일단 단순하게 자동매매를 구현하기 위해 복사해서 변수로 사용할거임
try:
    res = requests.post(url, headers=headers, json=body)
    data = res.json()
    print(data)
except Exception as e:
    print(e)
