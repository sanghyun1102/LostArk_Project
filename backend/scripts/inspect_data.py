import json
from pathlib import Path
import re
import html

def extract_tooltip_text(value):
    texts = []

    if isinstance(value, str):
        clean_text = re.sub(r"<[^>]+>", "", value)
        clean_text = html.unescape(clean_text)
        clean_text = clean_text.strip()

        if clean_text:
            texts.append(clean_text)

    elif isinstance(value, dict):
        for inner_value in value.values():
            texts.extend(
                extract_tooltip_text(inner_value)
            )

    elif isinstance(value, list):
        for inner_value in value:
            texts.extend(
                extract_tooltip_text(inner_value)
            )

    return texts

# data/raw 안에 있는 json 파일 찾기
json_files = list(Path("data/raw").glob("*.json"))

if not json_files:
    print("JSON 파일이 없습니다.")
    exit()

file_path = json_files[0]

print("불러온 파일:", file_path)

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)

""" print("\n=== 최상위 데이터 목록 ===")

for key in data.keys():
    value = data[key]

    if isinstance(value, list):
        print(f"{key}: 리스트 ({len(value)}개)")

    elif isinstance(value, dict):
        print(f"{key}: 객체 ({len(value)}개 항목)")

    elif value is None:
        print(f"{key}: 데이터 없음")

    else:
        print(f"{key}: {type(value).__name__}") """


""" print("\n=== ArmoryEquipment 장비 목록 ===")

equipment = data.get("ArmoryEquipment")

if equipment:
    for item in equipment:
        print(
            f"{item.get('Type')} | "
            f"{item.get('Name')} | "
            f"{item.get('Grade')}"
        )
else:
    print("ArmoryEquipment 데이터가 없습니다.") """

""" print("\n=== 첫 번째 장비 내부 구조 ===")

if equipment:
    first_item = equipment[0]

    for key, value in first_item.items():
        if key == "Tooltip":
            print(f"{key}: [내용이 길어서 생략]")
        else:
            print(f"{key}: {value}") """

""" print("\n=== 무기 Tooltip 타입 확인 ===")

if equipment:
    weapon = next(
        (item for item in equipment if item.get("Type") == "무기"),
        None
    )

    if weapon:
        tooltip = weapon.get("Tooltip")

        print("Tooltip Python 타입:", type(tooltip))
        print("\n=== 무기 Tooltip 원본 ===")
        print(tooltip) """

""" print("\n=== Tooltip JSON 변환 ===")

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
        print("Tooltip 변환 실패:", e) """


""" print("\n=== 무기 Tooltip 요소 구조 요약 ===")

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
            print(element) """

""" print("\n=== ArkPassive 구조 ===")

ark_passive_data = data.get("ArkPassive")

if ark_passive_data:

    for key, value in ark_passive_data.items():

        print(f"\n[{key}]")

        if isinstance(value, list):
            print(f"리스트 ({len(value)}개)")

            for index, item in enumerate(value):
                print(f"\n--- 항목 {index + 1} ---")

                if isinstance(item, dict):

                    for item_key, item_value in item.items():

                        if item_key in ("Tooltip", "ToolTip"):
                            print(f"{item_key}: [내용 생략]")
                        else:
                            print(f"{item_key}: {item_value}")

                else:
                    print(item)

        elif isinstance(value, dict):
            print("객체:")
            print(value)

        else:
            print(value)

else:
    print("ArkPassive 데이터가 없습니다.") """

""" print("\n=== ArkGrid 구조 ===")

arkgrid_data = data.get("ArkGrid")

if arkgrid_data:

    for key, value in arkgrid_data.items():

        print(f"\n[{key}]")

        if isinstance(value, list):
            print(f"리스트 ({len(value)}개)")

            for index, item in enumerate(value):

                print(f"\n--- 항목 {index + 1} ---")

                if isinstance(item, dict):

                    for item_key, item_value in item.items():

                        if item_key in ("Tooltip", "ToolTip"):
                            print(f"{item_key}: [내용 생략]")
                        else:
                            print(f"{item_key}: {item_value}")

                else:
                    print(item)

        elif isinstance(value, dict):

            print("객체:")

            for item_key, item_value in value.items():

                if item_key in ("Tooltip", "ToolTip"):
                    print(f"{item_key}: [내용 생략]")
                else:
                    print(f"{item_key}: {item_value}")

        else:
            print(value)

else:
    print("ArkGrid 데이터가 없습니다.") """

""" print("\n=== ArmoryCard 구조 ===")

card_data = data.get("ArmoryCard")

if card_data:

    for key, value in card_data.items():

        print(f"\n[{key}]")

        if isinstance(value, list):

            print(f"리스트 ({len(value)}개)")

            for index, item in enumerate(value):

                print(f"\n--- 항목 {index + 1} ---")

                if isinstance(item, dict):

                    for item_key, item_value in item.items():

                        if item_key in ("Tooltip", "ToolTip"):
                            print(
                                f"{item_key}: [내용 생략]"
                            )
                        else:
                            print(
                                f"{item_key}: {item_value}"
                            )

                else:
                    print(item)

        elif isinstance(value, dict):

            print("객체:")

            for item_key, item_value in value.items():

                if item_key in ("Tooltip", "ToolTip"):
                    print(
                        f"{item_key}: [내용 생략]"
                    )
                else:
                    print(
                        f"{item_key}: {item_value}"
                    )

        else:
            print(value)

else:
    print("ArmoryCard 데이터가 없습니다.") """

""" print("\n=== 액세서리 Tooltip 구조 ===")

accessory_types = [
    "목걸이",
    "귀걸이",
    "반지"
]

for item in data.get("ArmoryEquipment", []):

    if item.get("Type") not in accessory_types:
        continue

    print(
        f"\n[{item.get('Type')}] "
        f"{item.get('Name')}"
    )

    raw_tooltip = item.get("Tooltip")

    if not raw_tooltip:
        print("Tooltip 없음")
        continue

    try:
        tooltip = json.loads(raw_tooltip)

        for key, value in tooltip.items():

            print(f"\n{key}")

            if isinstance(value, dict):

                value_type = value.get("type")
                value_data = value.get("value")

                print("type:", value_type)

                # 너무 긴 데이터는 텍스트만 추출
                texts = extract_tooltip_text(
                    value_data
                )

                for text in texts:
                    print(" -", text)

            else:
                print(value)

    except json.JSONDecodeError:
        print("Tooltip JSON 변환 실패") """

""" print("\n=== 어빌리티 스톤 Tooltip 구조 ===")

for item in data.get("ArmoryEquipment", []):

    if item.get("Type") != "어빌리티 스톤":
        continue

    print(
        f"\n[{item.get('Type')}] "
        f"{item.get('Name')}"
    )

    raw_tooltip = item.get("Tooltip")

    if not raw_tooltip:
        print("Tooltip 없음")
        continue

    try:
        tooltip = json.loads(raw_tooltip)

        for key, value in tooltip.items():

            print(f"\n{key}")

            if isinstance(value, dict):

                print(
                    "type:",
                    value.get("type")
                )

                texts = extract_tooltip_text(
                    value.get("value")
                )

                for text in texts:
                    print(" -", text)

            else:
                print(value)

    except json.JSONDecodeError:
        print("Tooltip JSON 변환 실패") """

print("\n=== 팔찌 Tooltip 구조 ===")

for item in data.get("ArmoryEquipment", []):

    if item.get("Type") != "팔찌":
        continue

    print(
        f"\n[{item.get('Type')}] "
        f"{item.get('Name')}"
    )

    raw_tooltip = item.get("Tooltip")

    if not raw_tooltip:
        print("Tooltip 없음")
        continue

    try:
        tooltip = json.loads(raw_tooltip)

        for key, value in tooltip.items():

            print(f"\n{key}")

            if isinstance(value, dict):

                print(
                    "type:",
                    value.get("type")
                )

                texts = extract_tooltip_text(
                    value.get("value")
                )

                for text in texts:
                    print(" -", text)

            else:
                print(value)

    except json.JSONDecodeError:
        print("Tooltip JSON 변환 실패")