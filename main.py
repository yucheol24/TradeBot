from time import sleep
import requests
from dotenv import load_dotenv
import os

from api_test import ACCESS_TOKEN

load_dotenv()

BASE_URL = "https://openapivts.koreainvestment.com:29443"
APPKEY = os.environ["APPKEY"]
APPSECRET = os.environ["APPSECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]

# 자동 매매를 할 주식 종목 코드를 정해두고 쓰려고 변수에 저장
CODE = "005930"     # 삼성전자

# 이전 backtest.py, api_test.py에서 작성했던 함수들 추가
def ma(values, window_size):
    if len(values) >= window_size:
        target_values = values[-window_size:]
        return sum(target_values) / window_size
    else:
        return None

def ma_signal(ma_short_term, ma_long_term):
    if len(ma_short_term) < 2 or len(ma_long_term) < 2:
        return None
    if None in ma_short_term[-2:] or None in ma_long_term[-2:]:
        return None
    prev = ma_short_term[-2] - ma_long_term[-2]
    current = ma_short_term[-1] - ma_long_term[-1]
    if prev < 0 and current >= 0:
        return "BUY"
    elif prev >= 0 and current < 0:
        return "SELL"
    else:
        return None

def fetch_current_price(code):
    url = f"{BASE_URL}/uapi/domestic-stock/v1/quotations/inquire-price"
    headers = {
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APPKEY,
        "appsecret": APPSECRET,
        "tr_id": "FHKST01010100"
    }
    params = {
        "FID_COND_MRKT_DIV_CODE": "J",
        "FID_INPUT_ISCD": code
    }
    res = requests.get(url, headers=headers, params=params)
    try:
        data = res.json()
        return int(data["output"]["stck_prpr"])
    except Exception as e:
        print(e)
        return None

# 자동 매매 코드

prices = []
ma20 = []
ma60 = []

# 이 코드는 1분마다 현재가를 받아오기 때문에, 주식 정규장이 열려 있을 때만 제대로 동작함
while True:
    # 현재 가격 조회
    current_price = fetch_current_price(CODE)
    if current_price is not None:
        prices.append(current_price)
        # 이동 평균선 계산
        ma20.append(ma(prices, 20))
        ma60.append(ma(prices, 60))
        # 투자 전략 확인
        signal = ma_signal(ma20, ma60)
        print(f"가격: {prices[-1]} MA20: {ma20[-1]} MA60: {ma60[-1]} 신호: {signal}")
        # 과거 주문을 조회하고 미체결된 주문이 있으면 취소하기
        # 매수 주문 가능한 수량 조회하기
        # 보유 수량 업데이트하기
    # 전략에 따라 주문하기
    sleep(60)