import json

# MA20, MA60 값 리턴 함수
def get_stck_prpr(ma_value):
    ma_list = []
    for i in range(ma_value, len(stck_prpr_values)):
        avg = sum(stck_prpr_values[i-ma_value:i]) / ma_value
        ma_list.append(round(avg, 2))
    return ma_list

data = None
# sample.json 데이터 읽기
with open("sample.json", "r") as f:
    data = json.load(f)

# 리스트에 불러온 현재가 저장
stck_prpr_values = [int(item.get("stck_prpr")) for item in data]

print(stck_prpr_values)

MA20 = get_stck_prpr(20)
MA60 = get_stck_prpr(60)

print(MA20)
print(MA60)
