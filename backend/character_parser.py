import json
import re
import html
from pathlib import Path

def parse_weapon(equipment):
    weapon = next(
        (item for item in equipment if item.get("Type") == "무기"),
        None
    )

    if not weapon:
        return None

    tooltip = json.loads(weapon["Tooltip"])

    # 강화 단계
    enhancement_level = None

    match = re.match(r"\+(\d+)", weapon["Name"])

    if match:
        enhancement_level = int(match.group(1))


    # 기본값
    item_level = None
    quality = None
    weapon_attack = None
    additional_damage = None


    # Element_001 : 아이템 레벨 / 품질
    item_title = tooltip.get("Element_001", {}).get("value")

    if isinstance(item_title, dict):

        quality = item_title.get("qualityValue")

        level_text = item_title.get("leftStr2", "")

        level_match = re.search(r"아이템 레벨\s*(\d+)", level_text)

        if level_match:
            item_level = int(level_match.group(1))


    # Element_004 : 무기 공격력
    basic_effect = tooltip.get("Element_004", {}).get("value")

    if isinstance(basic_effect, dict):

        attack_text = basic_effect.get("Element_001", "")

        attack_match = re.search(r"무기 공격력\s*\+(\d+)", attack_text)

        if attack_match:
            weapon_attack = int(attack_match.group(1))


    # Element_006 : 추가 피해
    additional_effect = tooltip.get("Element_006", {}).get("value")

    if isinstance(additional_effect, dict):

        damage_text = additional_effect.get("Element_001", "")

        damage_match = re.search(r"추가 피해\s*\+([\d.]+)%", damage_text)

        if damage_match:
            additional_damage = float(damage_match.group(1))


    return {
        "name": weapon["Name"],
        "grade": weapon["Grade"],
        "enhancement_level": enhancement_level,
        "item_level": item_level,
        "quality": quality,
        "weapon_attack": weapon_attack,
        "additional_damage": additional_damage
    }

def parse_armor(equipment):
    armor_types = ["투구", "상의", "하의", "장갑", "어깨"]

    armor_list = []

    for item in equipment:

        if item.get("Type") not in armor_types:
            continue

        tooltip = json.loads(item["Tooltip"])

        enhancement_level = None
        item_level = None
        quality = None

        # 강화 단계
        match = re.match(r"\+(\d+)", item["Name"])

        if match:
            enhancement_level = int(match.group(1))

        # Tooltip 전체를 확인
        for element in tooltip.values():

            if not isinstance(element, dict):
                continue

            value = element.get("value")

            # 아이템 레벨 / 품질
            if isinstance(value, dict):

                # 품질
                if "qualityValue" in value:
                    quality = value.get("qualityValue")

                # 아이템 레벨
                for inner_value in value.values():

                    if isinstance(inner_value, str):

                        level_match = re.search(
                            r"아이템 레벨\s*(\d+)",
                            inner_value
                        )

                        if level_match:
                            item_level = int(level_match.group(1))

        armor_data = {
            "type": item["Type"],
            "name": item["Name"],
            "grade": item["Grade"],
            "enhancement_level": enhancement_level,
            "item_level": item_level,
            "quality": quality
        }

        armor_list.append(armor_data)

    return armor_list

def extract_tooltip_text(value):
    texts = []

    if isinstance(value, str):
        # HTML 태그 제거
        clean_text = re.sub(r"<[^>]+>", "", value)

        # &lt; 등의 HTML 문자 변환
        clean_text = html.unescape(clean_text)

        clean_text = clean_text.strip()

        if clean_text:
            texts.append(clean_text)

    elif isinstance(value, dict):
        for inner_value in value.values():
            texts.extend(extract_tooltip_text(inner_value))

    elif isinstance(value, list):
        for inner_value in value:
            texts.extend(extract_tooltip_text(inner_value))

    return texts

def clean_html_text(text):
    if not isinstance(text, str):
        return text

    return re.sub(r"<[^>]+>", "", text).strip()

def parse_skill_gems(skill_gem_data):
    if not skill_gem_data:
        return None

    raw_skill_gems = skill_gem_data.get("Gems", [])
    effects = skill_gem_data.get("Effects", {})

    skill_effects = effects.get("Skills", [])

    # GemSlot을 기준으로 스킬 효과를 찾기 쉽게 변환
    effect_by_slot = {}

    for effect in skill_effects:
        slot = effect.get("GemSlot")

        effect_by_slot[slot] = {
            "skill_name": effect.get("Name"),
            "description": effect.get("Description"),
            "option": effect.get("Option")
        }

    parsed_skill_gems = []

    for skill_gem in raw_skill_gems:
        slot = skill_gem.get("Slot")

        raw_name = clean_html_text(skill_gem.get("Name", ""))

        # 겁화 / 작열 구분
        skill_gem_type = None

        if "겁화" in raw_name:
            skill_gem_type = "겁화"

        elif "작열" in raw_name:
            skill_gem_type = "작열"

        effect = effect_by_slot.get(slot, {})

        parsed_skill_gem = {
            "slot": slot,
            "type": skill_gem_type,
            "level": skill_gem.get("Level"),
            "grade": skill_gem.get("Grade"),
            "skill_name": effect.get("skill_name"),
            "effect_description": effect.get("description"),
            "attack_option": effect.get("option")
        }

        parsed_skill_gems.append(parsed_skill_gem)

    return {
        "gems": parsed_skill_gems,
        "total_effect": clean_html_text(
            effects.get("Description", "")
        )
    }

def parse_engravings(engraving_data):
    if not engraving_data:
        return []

    ark_passive_effects = engraving_data.get("ArkPassiveEffects")

    if not ark_passive_effects:
        return []

    parsed_engravings = []

    for engraving in ark_passive_effects:

        parsed_engraving = {
            "name": engraving.get("Name"),
            "level": engraving.get("Level"),
            "grade": engraving.get("Grade"),
            "ability_stone_level": engraving.get("AbilityStoneLevel"),
            "description": clean_html_text(
                engraving.get("Description", "")
            )
        }

        parsed_engravings.append(parsed_engraving)

    return parsed_engravings

json_files = list(Path("data/raw").glob("*.json"))

if not json_files:
    print("JSON 파일이 없습니다.")
    exit()

file_path = json_files[0]

with open(file_path, "r", encoding="utf-8") as file:
    data = json.load(file)


profile = data["ArmoryProfile"]
equipment = data["ArmoryEquipment"]

# 전투 특성을 Dictionary 형태로 변환
stats = {}

for stat in profile["Stats"]:
    stat_type = stat["Type"]
    stat_value = stat["Value"]

    stats[stat_type] = stat_value


character = {
    "character_name": profile["CharacterName"],
    "server_name": profile["ServerName"],
    "class_name": profile["CharacterClassName"],
    "character_level": profile["CharacterLevel"],
    "item_level": profile["ItemAvgLevel"],
    "combat_power": profile["CombatPower"],

    "crit": stats.get("치명"),
    "specialization": stats.get("특화"),
    "swiftness": stats.get("신속"),

    "attack_power": stats.get("공격력"),
    "max_hp": stats.get("최대 생명력")
}


print("=== 캐릭터 분석 데이터 ===")

for key, value in character.items():
    print(f"{key}: {value}")

weapon_data = parse_weapon(equipment)

print("\n=== 무기 분석 데이터 ===")

for key, value in weapon_data.items():
    print(f"{key}: {value}")

armor_data = parse_armor(equipment)

print("\n=== 방어구 분석 데이터 ===")

for armor in armor_data:
    print(
        f"{armor['type']} | "
        f"강화 +{armor['enhancement_level']} | "
        f"아이템 레벨 {armor['item_level']} | "
        f"품질 {armor['quality']}"
    )

enhancement_values = [
    armor["enhancement_level"]
    for armor in armor_data
    if armor["enhancement_level"] is not None
]

quality_values = [
    armor["quality"]
    for armor in armor_data
    if armor["quality"] is not None
]

if enhancement_values:
    average_enhancement = sum(enhancement_values) / len(enhancement_values)

    print(
        "\n평균 방어구 강화:",
        round(average_enhancement, 2)
    )

if quality_values:
    average_quality = sum(quality_values) / len(quality_values)

    print(
        "평균 방어구 품질:",
        round(average_quality, 2)
    )

skill_gem_data = data.get("ArmoryGem")

parsed_skill_gem_data = parse_skill_gems(skill_gem_data)

print("\n=== 스킬 보석 분석 데이터 ===")

for skill_gem in parsed_skill_gem_data["gems"]:
    print(
        f"슬롯 {skill_gem['slot']} | "
        f"{skill_gem['type']} {skill_gem['level']}레벨 | "
        f"{skill_gem['skill_name']} | "
        f"{skill_gem['effect_description']}"
    )

print(
    "\n전체 효과:",
    parsed_skill_gem_data["total_effect"]
)

skill_gems = parsed_skill_gem_data["gems"]

levels = [
    skill_gem["level"]
    for skill_gem in skill_gems
    if skill_gem["level"] is not None
]

if levels:
    average_level = sum(levels) / len(levels)

    print("\n스킬 보석 개수:", len(levels))
    print("평균 스킬 보석 레벨:", round(average_level, 2))

print("\n=== ArmoryEngraving 구조 ===")

engraving_data = data.get("ArmoryEngraving")

parsed_engravings = parse_engravings(engraving_data)

print("\n=== 각인 분석 데이터 ===")

for engraving in parsed_engravings:

    stone_text = ""

    if engraving["ability_stone_level"] is not None:
        stone_text = (
            f" | 어빌리티 스톤 Lv."
            f"{engraving['ability_stone_level']}"
        )

    print(
        f"{engraving['name']} | "
        f"Lv.{engraving['level']} | "
        f"{engraving['grade']}"
        f"{stone_text}"
    )