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

sample_prices = load_prices("sample.json")
print(sample_prices)