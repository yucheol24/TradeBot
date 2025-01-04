from time import sleep
import requests
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

BASE_URL = "https://openapivts.koreainvestment.com:29443"
APPKEY = os.environ["APPKEY"]
APPSECRET = os.environ["APPSECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]

# 자동 매매를 할 주식 종목 코드를 정해두고 쓰려고 변수에 저장
CODE = "005930"     # 삼성전자
ACCOUNT = os.environ["ACCOUNT"]     # 국내주식 계좌
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

# 주문 체결 조회 함수
def fetch_orders(account, code):
    today = datetime.today().strftime('%Y%m%d')
    url = f"{BASE_URL}/uapi/domestic-stock/v1/trading/inquire-daily-ccld"
    headers = {
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": {APPKEY},
        "appsecret": {APPSECRET},
        "tr_id": "VTTC8001R"
    }
    params = {
        "CANO": account[:8],
        "ACNT_PRDT_CD": account[-2:],
        "INQR_STRT_DT": today,
        "INQR_END_DT": today,
        "SLL_BUY_DVSN_CD": 00,
        "INQR_DVSN": 00,
        "PDN0": code,
        "CCLD_DVSN": "02",  # 미체결
        "ORD_GNO_BRNO": "",
        "ODNO": "",
        "INQR_DVSN_3": 00,
        "INQR_DVSN_1": "",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    try:
        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        return data["output1"]
    except Exception as e:
        print(e)
        return []

# 주문 취소 함수
def cancel_order(account, order_no):
    url = f"{BASE_URL}/uapi/domestic-stock/v1/trading/order-rvsecncl"
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APPKEY,
        "appsecret": APPSECRET,
        "tr_id": "VTTC0803U"
    }
    body = {
        "CANO": account[:8],
        "ACNT_PRDT_CD": account[-2:],
        "KRX_FWDG_ORD_ORDNO": "",
        "ORGN_ODNO": order_no,
        "ORD_DVSN": "00",
        "RVSE_CNCL_DVSN_CD": "02",  # 취소
        "ORD_QTY": "0",  # 잔량전부 취소
        "ORD_UNPR": "0",  # 취소
        "QTY_ALL_ORD_YN": "Y",  # 잔량 전부
    }
    try:
        res = requests.post(url, headers=headers, json=body)
        data = res.json()
        return data["rt_cd"] == "0"     # 성공 실패 여부
    except Exception as e:
        print(e)
        return False

# 미체결 된 주식 취소 함수
def clear_order(account, code):
    orders = fetch_orders(account, code)
    for order in orders:
        order_no = order["odno"]
        result = cancel_order(account, order_no)
        print(f"{order_no} 취소 성공" if result else f"{order_no} 취소 실패")

# 매수 가능한 주식을 조회하는 함수
def fetch_avail(account, code, target_price):
    url = f"{BASE_URL}/uapi/domestic-stock/v1/trading/inquire-psbl-order"
    headers = {
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APPKEY,
        "appsecret": APPSECRET,
        "tr_id": "VTTC8908R"
    }
    params = {
        "CANO": account[:8],
        "ACNT_PRDT_CD": account[-2:],
        "PDNO": code,
        "ORD_UNPR": str(target_price),
        "ORD_DVSN": "00",  # 지정가
        "CMA_EVLU_AMT_ICLD_YN": "N",
        "OVRS_ICLD_YN": "N",
    }
    try:
        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        return int(data["output"]["nrcvb_buy_qty"]) # 미수 없는 매수 가능 수량
    except Exception as e:
        print(e)
        return 0

# 주식 보유 수량 조회 함수
def fetch_quantity(account, code):
    url = f"{BASE_URL}/uapi/domestic-stock/v1/trading/inquire-psbl-order"
    headers = {
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APPKEY,
        "appsecret": APPSECRET,
        "tr_id": "VTTC8908R"
    }
    params = {
        "CANO": account[:8],
        "ACNT_PRDT_CD": account[-2:],
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",
        "INQR_DVSN": "02",
        "UNPR_DVSN": "01",
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "00",
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    try:
        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        for item in data["output1"]:
            if item["pdno"] == code:
                return int(item("hldg_qty"))
        return 0
    except Exception as e:
        print(e)
        return 0

# 매수 또는 매도 주문 기능 추가
def order(order_type, account, code, amount, target_price):
    url = f"{BASE_URL}/uapi/domestic-stock/v1/trading/order-cash"
    headers = {
        "content-type": "application/json; charset=utf-8",
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APPKEY,
        "appsecret": APPSECRET,
        "tr_id": "VTTC0802U" if order_type == "BUY" else "VTTC0801U"  # 주식 현금 매수/매도 주문
    }
    body = {
        "CANO": account[:8],
        "ACNT_PRDT_CD": account[-2:],
        "PDNO": code,
        "ORD_DVSN": "00",  # 지정가
        "ORD_QTY": str(amount),
        "ORD_UNPR": str(target_price)
    }
    try:
        res = requests.post(url, headers=headers, json=body)
        data = res.json()
        return data["rt_cd"] == "0"
    except Exception as e:
        print(e)
        return False

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
        clear_order(ACCOUNT, CODE)
        # 매수 주문 가능한 수량 조회하기
        fetch_avail(ACCOUNT, CODE, 50000)
        # 보유 수량 업데이트하기
    # 전략에 따라 주문하기
    sleep(60)