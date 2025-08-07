import json
import os

# value_map.json 파일이 같은 폴더에 있다고 가정
json_path = os.path.join(os.path.dirname(__file__), "value_map.json")

with open(json_path, "r", encoding="utf-8") as f:
    value_map = json.load(f) 