from time import sleep
import indicator
import strategy
import api

# 이 코드는 모의 주식에서 쓰기위해 만들어졌습니다.
# 실제 거래소에서 자동 매매를 원하시면 BASE_URL을 실전 Domain 주소로 바꾸고
# 거래 ID인 tr_id 값을 [실전투자] 값으로 바꿔야 합니다. (한국 투자 증권 API 참고)
# 이 코드는 1분마다 현재가를 받아오기 때문에, 주식 정규장이 열려 있을 때만 제대로 동작합니다.
# 꼭 자신의 .env 파일을 만들어주세요.
# 자신의 APPKEY, APPSECRET, ACCOUNT, ACCESS_TOKEN 키를 넣어야 정상 작동 됨
# 만약 잘 작동되지 않는다면 ACCESS_TOKEN 값을 다시 불러와서 사용하면 됩니다. (get_token.py)

# 자동 매매를 할 주식 종목 코드를 정해두고 쓰려고 변수에 저장
CODE = "005930"     # 삼성전자

# 자동 매매 코드

prices = []
ma20 = []
ma60 = []

# 이 코드는 1분마다 현재가를 받아오기 때문에, 주식 정규장이 열려 있을 때만 제대로 동작함
while True:
    # 현재 가격 조회
    current_price = api.fetch_current_price(CODE)
    if current_price is not None:
        prices.append(current_price)
        # 이동 평균선 계산
        ma20.append(indicator.ma(prices, 20))
        ma60.append(indicator.ma(prices, 60))
        # 투자 전략 확인
        signal = strategy.ma_signal(ma20, ma60)
        print(f"가격: {prices[-1]} MA20: {ma20[-1]} MA60: {ma60[-1]} 신호: {signal}")
        # 과거 주문을 조회하고 미체결된 주문이 있으면 취소하기
        sleep(0.2)
        api.clear_order(api.ACCOUNT, CODE)
        # 전략에 따라 주문하기
        amount = 0
        if signal == "BUY":
            # 매수 가능한 수량 조회하기
            amount = api.fetch_avail(api.ACCOUNT, CODE, prices[-1])
        elif signal == "SELL":
            # 보유 수량 업데이트하기
            amount = api.fetch_quantity(api.ACCOUNT, CODE)
        if amount > 0:
            sleep(0.2)
            result = api.order(signal, api.ACCOUNT, CODE, amount, prices[-1])
            if result:
                print(f"{signal} {CODE} {amount}개 {prices[-1]}원 주문 성공")
    sleep(0.2)  # 오류를 줄이기 위한 딜레이
    eval = api.fetch_eval(api.ACCOUNT)
    print(f"총 평가금: {eval}")
    sleep(60)