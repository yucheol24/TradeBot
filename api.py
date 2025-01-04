import requests
from dotenv import load_dotenv
import os
from datetime import datetime

load_dotenv()

BASE_URL = "https://openapivts.koreainvestment.com:29443"
APPKEY = os.environ["APPKEY"]
APPSECRET = os.environ["APPSECRET"]
ACCESS_TOKEN = os.environ["ACCESS_TOKEN"]
ACCOUNT = os.environ["ACCOUNT"]     # 국내주식 계좌

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
        "appkey": APPKEY,
        "appsecret": APPSECRET,
        "tr_id": "VTTC8001R"
    }
    params = {
        "CANO": account[:8],
        "ACNT_PRDT_CD": account[-2:],
        "INQR_STRT_DT": today,
        "INQR_END_DT": today,
        "SLL_BUY_DVSN_CD": "00",
        "INQR_DVSN": "00",
        "PDNO": code,
        "CCLD_DVSN": "02",  # 미체결
        "ORD_GNO_BRNO": "",
        "ODNO": "",
        "INQR_DVSN_3": "00",
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
        "KRX_FWDG_ORD_ORGNO": "",
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
        return data["output"]["nrcvb_buy_qty"] # 미수 없는 매수 가능 수량
    except Exception as e:
        print(e)
        return 0

# 주식 보유 수량 조회 함수
def fetch_quantity(account, code):
    url = f"{BASE_URL}/uapi/domestic-stock/v1/trading/inquire-balance"
    headers = {
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APPKEY,
        "appsecret": APPSECRET,
        "tr_id": "VTTC8434R"    # 주식 잔고 조회
    }
    params = {
        "CANO": account[:8],
        "ACNT_PRDT_CD": account[-2:],
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "",   # 공란
        "INQR_DVSN": "02",  # 종목별
        "UNPR_DVSN": "01",  # 단가 구분 기본값
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "00",  # 전일 매매 포함
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    try:
        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        for item in data["output1"]:
            if item["pdno"] == code:
                return item["hldg_qty"]
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

# 총 평가금을 알려주는 함수
def fetch_eval(account):
    url = f"{BASE_URL}/uapi/domestic-stock/v1/trading/inquire-balance"
    headers = {
        "authorization": f"Bearer {ACCESS_TOKEN}",
        "appkey": APPKEY,
        "appsecret": APPSECRET,
        "tr_id": "VTTC8434R"  # 주식 잔고 조회
    }
    params = {
        "CANO": account[:8],
        "ACNT_PRDT_CD": account[-2:],
        "AFHR_FLPR_YN": "N",
        "OFL_YN": "", # 공란
        "INQR_DVSN": "02",  # 종목별
        "UNPR_DVSN": "01",  # 단가 구분 기본값
        "FUND_STTL_ICLD_YN": "N",
        "FNCG_AMT_AUTO_RDPT_YN": "N",
        "PRCS_DVSN": "00",  # 전일 매매 포함
        "CTX_AREA_FK100": "",
        "CTX_AREA_NK100": ""
    }
    try:
        res = requests.get(url, headers=headers, params=params)
        data = res.json()
        print(data)
        return data["output2"][0]["tot_evlu_amt"]
    except Exception as e:
        print(e)
        return None