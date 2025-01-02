import json

def load_prices(filename):
    data = {}
    result = []
    with open(filename, "r") as f:
        data = json.load(f)
        f.close()
    for item in data:
        current_price = int(item["stck_prpr"])
        result.append(current_price)

    return result

# 이동 평균선 계산하는 함수
def ma(values, size):
    if len(values) >= size:
        target_values = values[-size:]
        return sum(target_values) / size
    else:
        return None

# 매도 신호 반환하는 함수
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

# 백테스트
def backtest(prices, initial_balance):
    balance = initial_balance   # 초기 잔고
    quantity = 0    # 수량
    ma20 = []
    ma60 = []

    for i in range(len(prices)):
        ma20.append(ma(prices[:i+1], 20))
        ma60.append(ma(prices[:i+1], 60))
        signal = ma_signal(ma20, ma60)

        if signal == "BUY":
            amount = balance // prices[i]
            quantity += amount
            balance -= amount * prices[i]
        elif signal == "SELL":
            amount = quantity   # 전량 매도
            quantity -= amount
            balance += amount * prices[i]

        # 현재 수익률
        roi = ((balance + prices[i] * quantity) / initial_balance - 1) * 100    # %로 표기
        if signal is not None:
            print(f"신호: {signal} 수익률: {roi}% 매도 수량: {quantity}주 잔고: {balance}원")
sample_prices = load_prices("sample.json")
backtest(sample_prices, 10000000)