import json
from pathlib import Path


# data/raw 안에 있는 json 파일 찾기
json_files = list(Path("data/raw").glob("*.json"))

if not json_files:
    print("JSON 파일이 없습니다.")
    exit()

file_path = json_files[0]

print("불러온 파일:", file_path)

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

print("\n=== 최상위 데이터 목록 ===")

for key in data.keys():
    value = data[key]

    if isinstance(value, list):
        print(f"{key}: 리스트 ({len(value)}개)")

    elif isinstance(value, dict):
        print(f"{key}: 객체 ({len(value)}개 항목)")

    elif value is None:
        print(f"{key}: 데이터 없음")

    else:
        print(f"{key}: {type(value).__name__}")


print("\n=== ArmoryEquipment 장비 목록 ===")

equipment = data.get("ArmoryEquipment")

if equipment:
    for item in equipment:
        print(
            f"{item.get('Type')} | "
            f"{item.get('Name')} | "
            f"{item.get('Grade')}"
        )
else:
    print("ArmoryEquipment 데이터가 없습니다.")

print("\n=== 첫 번째 장비 내부 구조 ===")

if equipment:
    first_item = equipment[0]

    for key, value in first_item.items():
        if key == "Tooltip":
            print(f"{key}: [내용이 길어서 생략]")
        else:
            print(f"{key}: {value}")

print("\n=== 무기 Tooltip 타입 확인 ===")

if equipment:
    weapon = next(
        (item for item in equipment if item.get("Type") == "무기"),
        None
    )

    if weapon:
        tooltip = weapon.get("Tooltip")

        print("Tooltip Python 타입:", type(tooltip))
        print("\n=== 무기 Tooltip 원본 ===")
        print(tooltip)

print("\n=== Tooltip JSON 변환 ===")

if weapon:
    tooltip = weapon.get("Tooltip")

    try:
        tooltip_data = json.loads(tooltip)

        print("변환 성공")
        print("변환 후 타입:", type(tooltip_data))

        print("\n=== Tooltip 최상위 항목 ===")

        for key in tooltip_data.keys():
            print(key)

    except (json.JSONDecodeError, TypeError) as e:
        print("Tooltip 변환 실패:", e)


print("\n=== 무기 Tooltip 요소 구조 요약 ===")

if weapon:
    tooltip_data = json.loads(weapon["Tooltip"])

    for key, element in tooltip_data.items():
        print(f"\n[{key}]")

        if isinstance(element, dict):
            print("내부 키:", list(element.keys()))

            element_type = element.get("type")
            element_value = element.get("value")

            print("type:", element_type)

            # 너무 긴 값은 앞부분만 출력
            value_text = str(element_value)

            if len(value_text) > 300:
                value_text = value_text[:300] + "..."

            print("value:", value_text)

        else:
            print(element)