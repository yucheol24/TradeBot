import json
import indicator
import strategy

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

# 백테스트
def backtest(prices, initial_balance):
    balance = initial_balance   # 초기 잔고
    quantity = 0    # 수량
    ma20 = []
    ma60 = []

    for i in range(len(prices)):
        ma20.append(indicator.ma(prices[:i+1], 20))
        ma60.append(indicator.ma(prices[:i+1], 60))
        signal = strategy.ma_signal(ma20, ma60)

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