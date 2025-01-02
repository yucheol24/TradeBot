import json

data = None
with open("sample.json", "r") as f:
    data = json.load(f)

stck_prpr_values = [int(item.get("stck_prpr")) for item in data]

print(stck_prpr_values)