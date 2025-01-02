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

sample_prices = load_prices("sample.json")
print(sample_prices)