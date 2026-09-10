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
        "name": weapon.get("Name"),
        "icon": weapon.get("Icon"),
        "grade": weapon.get("Grade"),

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
            "icon": item.get("Icon"),
            "enhancement_level": enhancement_level,
            "item_level": item_level,
            "quality": quality
        }

        armor_list.append(armor_data)

    return armor_list

def parse_wristguard(equipment):
    wristguard = next(
        (
            item
            for item in equipment
            if item.get("Type") == "완갑"
        ),
        None
    )

    if not wristguard:
        return None

    enhancement_level = None
    item_level = None
    item_tier = None
    quality = None

    # 강화 단계
    enhancement_match = re.search(
        r"\+(\d+)",
        wristguard.get("Name", "")
    )

    if enhancement_match:
        enhancement_level = int(
            enhancement_match.group(1)
        )

    raw_tooltip = wristguard.get("Tooltip")

    if raw_tooltip:
        try:
            tooltip = json.loads(raw_tooltip)
        except (json.JSONDecodeError, TypeError):
            tooltip = {}

        item_title = (
            tooltip
            .get("Element_001", {})
            .get("value", {})
        )

        if isinstance(item_title, dict):
            quality = item_title.get("qualityValue")

            for text in extract_tooltip_text(item_title):

                level_match = re.search(
                    r"아이템 레벨\s*(\d+)",
                    text
                )

                if level_match:
                    item_level = int(
                        level_match.group(1)
                    )

                tier_match = re.search(
                    r"티어\s*(\d+)",
                    text
                )

                if tier_match:
                    item_tier = int(
                        tier_match.group(1)
                    )

    return {
        "name": wristguard.get("Name"),
        "icon": wristguard.get("Icon"),
        "grade": wristguard.get("Grade"),

        "enhancement_level": enhancement_level,
        "item_level": item_level,
        "item_tier": item_tier,
        "quality": quality
    }

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
        return {
            "gems": [],
            "total_effect": None
        }

    raw_skill_gems = skill_gem_data.get("Gems") or []
    effects = skill_gem_data.get("Effects") or {}

    effect_by_slot = {}

    for skill in effects.get("Skills") or []:
        gem_slot = skill.get("GemSlot")

        effect_by_slot[gem_slot] = {
            "skill_name": skill.get("Name"),
            "description": skill.get("Description"),
            "option": skill.get("Option")
        }

    parsed_skill_gems = []

    for skill_gem in raw_skill_gems:
        slot = skill_gem.get("Slot")

        gem_name = clean_html_text(
            skill_gem.get("Name", "")
        )

        skill_gem_type = None

        if "겁화" in gem_name:
            skill_gem_type = "겁화"

        elif "작열" in gem_name:
            skill_gem_type = "작열"

        elif "광휘" in gem_name:
            skill_gem_type = "광휘"

        else:
            skill_gem_type = "기타"
            
        effect = effect_by_slot.get(
            slot,
            {}
        )

        parsed_skill_gems.append({
            "slot": slot,
            "icon": skill_gem.get("Icon"),
            "type": skill_gem_type,
            "level": skill_gem.get("Level"),
            "grade": skill_gem.get("Grade"),
            "skill_name": effect.get("skill_name"),
            "effect_description": effect.get("description"),
            "attack_option": effect.get("option")
        })

    return {
        "gems": parsed_skill_gems,
        "total_effect": clean_html_text(
            effects.get("Description", "")
        )
    }
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

def parse_ark_passive(ark_passive_data):
    if not ark_passive_data:
        return None

    # ==============================
    # 1. 포인트 정보
    # ==============================

    parsed_points = {}

    for point in ark_passive_data.get("Points", []):

        name = point.get("Name")
        description = point.get("Description", "")

        rank = None
        level = None

        rank_match = re.search(
            r"(\d+)랭크\s*(\d+)레벨",
            description
        )

        if rank_match:
            rank = int(rank_match.group(1))
            level = int(rank_match.group(2))

        parsed_points[name] = {
            "value": point.get("Value"),
            "rank": rank,
            "level": level
        }

    # ==============================
    # 2. 활성화된 노드 정보
    # ==============================

    parsed_effects = []

    for effect in ark_passive_data.get("Effects", []):

        effect_type = effect.get("Name")

        description = clean_html_text(
            effect.get("Description", "")
        )

        tier = None
        node_name = None
        node_level = None

        # 예:
        # 깨달음 1티어 피냄새 Lv.3
        # 진화 5티어 뭉툭한 가시 Lv.2
        match = re.search(
            r"(?:진화|깨달음|도약)\s*"
            r"(\d+)티어\s*"
            r"(.+?)\s*"
            r"Lv\.(\d+)",
            description
        )

        if match:
            tier = int(match.group(1))
            node_name = match.group(2).strip()
            node_level = int(match.group(3))

        # ==============================
        # Tooltip 상세 효과
        # ==============================

        effect_detail = None

        raw_tooltip = effect.get("ToolTip")

        if raw_tooltip:

            try:
                tooltip_data = json.loads(raw_tooltip)

                detail_html = (
                    tooltip_data
                    .get("Element_002", {})
                    .get("value", "")
                )

                effect_detail = clean_html_text(
                    detail_html
                )

                effect_detail = (
                    effect_detail
                    .replace("||", " ")
                    .strip()
                )

            except (json.JSONDecodeError, TypeError):
                effect_detail = None

        parsed_effect = {
            "type": effect_type,
            "tier": tier,
            "name": node_name,
            "level": node_level,
            "icon": effect.get("Icon"),
            "description": effect_detail
        }

        parsed_effects.append(parsed_effect)

    return {
        "title": ark_passive_data.get("Title"),
        "enabled": ark_passive_data.get("IsArkPassive"),
        "points": parsed_points,
        "effects": parsed_effects
    }

def parse_arkgrid_gem(arkgrid_gem):
    if not arkgrid_gem:
        return None

    raw_tooltip = arkgrid_gem.get("Tooltip")

    if not raw_tooltip:
        return None

    try:
        tooltip = json.loads(raw_tooltip)

    except (json.JSONDecodeError, TypeError):
        return None

    # ------------------------------
    # 젬 이름
    # ------------------------------

    name = None

    name_html = (
        tooltip
        .get("Element_000", {})
        .get("value", "")
    )

    if name_html:
        name = clean_html_text(name_html)

    # 예:
    # 질서의 젬 : 안정

    gem_type = None
    gem_name = None

    if name:

        name_match = re.search(
            r"(질서|혼돈)의 젬\s*:\s*(.+)",
            name
        )

        if name_match:
            gem_type = name_match.group(1)
            gem_name = name_match.group(2).strip()

    # ------------------------------
    # 젬 기본 정보
    # ------------------------------

    gem_point = None

    basic_info = (
        tooltip
        .get("Element_004", {})
        .get("value", {})
    )

    if isinstance(basic_info, dict):

        basic_text = basic_info.get(
            "Element_001",
            ""
        )

        point_match = re.search(
            r"젬 포인트\s*:\s*"
            r"(?:<[^>]+>)*"
            r"(\d+)",
            basic_text
        )

        if point_match:
            gem_point = int(
                point_match.group(1)
            )

    # ------------------------------
    # 젬 효과
    # ------------------------------

    required_willpower = None
    core_point = None
    options = []

    effect_info = (
        tooltip
        .get("Element_005", {})
        .get("value", {})
    )

    if isinstance(effect_info, dict):

        effect_html = effect_info.get(
            "Element_001",
            ""
        )

        # HTML 태그를 공백으로 변환
        effect_text = re.sub(
            r"<[^>]+>",
            " ",
            effect_html
        )

        effect_text = re.sub(
            r"\s+",
            " ",
            effect_text
        ).strip()

        # 필요 의지력
        willpower_match = re.search(
            r"필요 의지력\s*:\s*(\d+)",
            effect_text
        )

        if willpower_match:
            required_willpower = int(
                willpower_match.group(1)
            )

        # 질서/혼돈 포인트
        core_point_match = re.search(
            r"(?:질서|혼돈) 포인트\s*:\s*(\d+)",
            effect_text
        )

        if core_point_match:
            core_point = int(
                core_point_match.group(1)
            )

        # 옵션
        option_matches = re.findall(
            r"\[([^\]]+)\]\s*"
            r"Lv\.(\d+)",
            effect_text
        )

        for option_name, option_level in option_matches:

            options.append({
                "name": option_name,
                "level": int(option_level)
            })

    return {
        "index": arkgrid_gem.get("Index"),
        "icon": arkgrid_gem.get("Icon"),
        "active": arkgrid_gem.get("IsActive"),
        "grade": arkgrid_gem.get("Grade"),

        "type": gem_type,
        "name": gem_name,

        "gem_point": gem_point,
        "required_willpower": required_willpower,
        "core_point": core_point,

        "options": options
    }

def parse_arkgrid(arkgrid_data):
    if not arkgrid_data:
        return None

    parsed_cores = []

    # ==============================
    # 코어
    # ==============================

    for core in arkgrid_data.get("Slots", []):

        parsed_gems = []

        for arkgrid_gem in core.get("Gems", []):

            parsed_gem = parse_arkgrid_gem(
                arkgrid_gem
            )

            if parsed_gem:
                parsed_gems.append(
                    parsed_gem
                )

        parsed_core = {
            "index": core.get("Index"),
            "name": core.get("Name"),
            "icon": core.get("Icon"),
            "point": core.get("Point"),
            "grade": core.get("Grade"),
            "gems": parsed_gems
        }

        parsed_cores.append(
            parsed_core
        )

    # ==============================
    # 전체 효과
    # ==============================

    parsed_effects = []

    for effect in arkgrid_data.get(
        "Effects",
        []
    ):

        parsed_effects.append({
            "name": effect.get("Name"),
            "level": effect.get("Level")
        })

    return {
        "cores": parsed_cores,
        "effects": parsed_effects
    }

def parse_cards(card_data):
    if not card_data:
        return None

    parsed_cards = []

    # ==============================
    # 장착 카드
    # ==============================

    for card in card_data.get("Cards", []):

        parsed_card = {
            "slot": card.get("Slot"),
            "name": card.get("Name"),
            "icon": card.get("Icon"),
            "awake_count": card.get("AwakeCount"),
            "awake_total": card.get("AwakeTotal"),
            "grade": card.get("Grade")
        }

        parsed_cards.append(parsed_card)

    # ==============================
    # 총 각성 수
    # ==============================

    total_awake = sum(
        card["awake_count"] or 0
        for card in parsed_cards
    )

    # ==============================
    # 활성화 카드 세트 효과
    # ==============================

    parsed_effects = []

    for effect_group in card_data.get(
        "Effects",
        []
    ):

        for item in effect_group.get(
            "Items",
            []
        ):

            parsed_effect = {
                "name": item.get("Name"),
                "description": item.get(
                    "Description"
                )
            }

            parsed_effects.append(
                parsed_effect
            )

    return {
        "cards": parsed_cards,
        "total_awake": total_awake,
        "effects": parsed_effects
    }

def split_tooltip_lines(text):
    if not isinstance(text, str):
        return []

    # <br>, <BR> 등을 줄바꿈으로 변환
    text = re.sub(
        r"<br\s*/?>",
        "\n",
        text,
        flags=re.IGNORECASE
    )

    # 나머지 HTML 태그 제거
    text = re.sub(
        r"<[^>]+>",
        "",
        text
    )

    text = html.unescape(text)

    return [
        line.strip()
        for line in text.split("\n")
        if line.strip()
    ]

def parse_accessory_item(accessory):
    raw_tooltip = accessory.get("Tooltip")

    if not raw_tooltip:
        return None

    try:
        tooltip = json.loads(raw_tooltip)

    except (json.JSONDecodeError, TypeError):
        return None

    # ==============================
    # 품질 / 티어
    # ==============================

    quality = None
    item_tier = None

    item_title = (
        tooltip
        .get("Element_001", {})
        .get("value", {})
    )

    if isinstance(item_title, dict):

        quality = item_title.get(
            "qualityValue"
        )

        title_texts = extract_tooltip_text(
            item_title
        )

        for text in title_texts:

            tier_match = re.search(
                r"아이템 티어\s*(\d+)",
                text
            )

            if tier_match:
                item_tier = int(
                    tier_match.group(1)
                )

    # ==============================
    # 기본 효과
    # ==============================

    base_stats = {}

    base_effect = (
        tooltip
        .get("Element_004", {})
        .get("value", {})
    )

    if isinstance(base_effect, dict):

        base_text = base_effect.get(
            "Element_001",
            ""
        )

        for stat_name in [
            "힘",
            "민첩",
            "지능",
            "체력"
        ]:

            match = re.search(
                rf"{stat_name}\s*\+(\d+)",
                base_text
            )

            if match:
                base_stats[stat_name] = int(
                    match.group(1)
                )

    # ==============================
    # 연마 효과
    # ==============================

    polishing_effects = []

    polishing = (
        tooltip
        .get("Element_006", {})
        .get("value", {})
    )

    if isinstance(polishing, dict):

        polishing_text = polishing.get(
            "Element_001",
            ""
        )

        lines = split_tooltip_lines(
            polishing_text
        )

        for line in lines:

            match = re.search(
                r"(.+?)\s*\+"
                r"(\d+(?:\.\d+)?)"
                r"(%?)$",
                line
            )

            if match:

                effect_name = (
                    match.group(1).strip()
                )

                value = float(
                    match.group(2)
                )

                unit = match.group(3)

                # 390 같은 정수는 int 처리
                if not unit and value.is_integer():
                    value = int(value)

                polishing_effects.append({
                    "name": effect_name,
                    "value": value,
                    "unit": unit
                })

    # ==============================
    # 깨달음 포인트
    # ==============================

    enlightenment_point = None

    ark_passive_effect = (
        tooltip
        .get("Element_007", {})
        .get("value", {})
    )

    if isinstance(
        ark_passive_effect,
        dict
    ):

        ark_text = ark_passive_effect.get(
            "Element_001",
            ""
        )

        ark_text = clean_html_text(
            ark_text
        )

        enlightenment_match = re.search(
            r"깨달음\s*\+(\d+)",
            ark_text
        )

        if enlightenment_match:

            enlightenment_point = int(
                enlightenment_match.group(1)
            )

    return {
        "type": accessory.get("Type"),
        "name": accessory.get("Name"),
        "icon": accessory.get("Icon"),
        "grade": accessory.get("Grade"),

        "quality": quality,
        "item_tier": item_tier,

        "base_stats": base_stats,

        "polishing_effects": polishing_effects,

        "enlightenment_point":
            enlightenment_point
    }

def parse_accessories(equipment):
    accessory_types = [
        "목걸이",
        "귀걸이",
        "반지"
    ]

    parsed_accessories = []

    for item in equipment:

        if item.get("Type") not in accessory_types:
            continue

        parsed_accessory = (
            parse_accessory_item(item)
        )

        if parsed_accessory:
            parsed_accessories.append(
                parsed_accessory
            )

    return parsed_accessories

def parse_ability_stone(equipment):
    ability_stone = next(
        (
            item
            for item in equipment
            if item.get("Type") == "어빌리티 스톤"
        ),
        None
    )

    if not ability_stone:
        return None

    raw_tooltip = ability_stone.get("Tooltip")

    if not raw_tooltip:
        return None

    try:
        tooltip = json.loads(raw_tooltip)

    except (json.JSONDecodeError, TypeError):
        return None

    # ==============================
    # 티어
    # ==============================

    item_tier = None

    item_title = (
        tooltip
        .get("Element_001", {})
        .get("value", {})
    )

    if isinstance(item_title, dict):

        title_texts = extract_tooltip_text(
            item_title
        )

        for text in title_texts:

            tier_match = re.search(
                r"아이템 티어\s*(\d+)",
                text
            )

            if tier_match:
                item_tier = int(
                    tier_match.group(1)
                )

    # ==============================
    # 기본 체력
    # ==============================

    base_hp = None

    base_effect = (
        tooltip
        .get("Element_004", {})
        .get("value", {})
    )

    if isinstance(base_effect, dict):

        base_text = base_effect.get(
            "Element_001",
            ""
        )

        hp_match = re.search(
            r"체력\s*\+(\d+)",
            base_text
        )

        if hp_match:
            base_hp = int(
                hp_match.group(1)
            )

    # ==============================
    # 세공 보너스 체력
    # ==============================

    bonus_hp = None

    bonus_effect = (
        tooltip
        .get("Element_006", {})
        .get("value", {})
    )

    if isinstance(bonus_effect, dict):

        bonus_text = bonus_effect.get(
            "Element_001",
            ""
        )

        hp_match = re.search(
            r"체력\s*\+(\d+)",
            bonus_text
        )

        if hp_match:
            bonus_hp = int(
                hp_match.group(1)
            )

    # ==============================
    # 각인 / 레벨 보너스
    # ==============================

    engravings = []
    level_bonus = None

    engraving_data = (
        tooltip
        .get("Element_007", {})
        .get("value")
    )

    engraving_texts = extract_tooltip_text(
        engraving_data
    )

    for text in engraving_texts:

        engraving_match = re.search(
            r"\[(.+?)\]\s*Lv\.(\d+)",
            text
        )

        if engraving_match:

            engraving_name = (
                engraving_match
                .group(1)
                .strip()
            )

            engraving_level = int(
                engraving_match.group(2)
            )

            engravings.append({
                "name": engraving_name,
                "level": engraving_level
            })

        bonus_match = re.search(
            r"\[레벨 보너스\]\s*(.+)",
            text
        )

        if bonus_match:
            level_bonus = (
                bonus_match
                .group(1)
                .strip()
            )

    return {
        "name": ability_stone.get("Name"),
        "icon": ability_stone.get("Icon"),
        "grade": ability_stone.get("Grade"),
        "item_tier": item_tier,

        "base_hp": base_hp,
        "bonus_hp": bonus_hp,

        "engravings": engravings,
        "level_bonus": level_bonus
    }

def parse_profile(profile):
    if not profile:
        return None

    stats = {
        stat["Type"]: stat["Value"]
        for stat in profile.get("Stats", [])
    }

    return {
        "character_name": profile.get("CharacterName"),
        "character_image": profile.get("CharacterImage"),
        "server_name": profile.get("ServerName"),
        "class_name": profile.get("CharacterClassName"),

        "character_level": to_int(
            profile.get("CharacterLevel")
        ),

        "item_level": to_float(
            profile.get("ItemAvgLevel")
        ),

        "combat_power": to_float(
            profile.get("CombatPower")
        ),

        "crit": to_int(
            stats.get("치명")
        ),

        "specialization": to_int(
            stats.get("특화")
        ),

        "swiftness": to_int(
            stats.get("신속")
        ),

        "attack_power": to_int(
            stats.get("공격력")
        ),

        "max_hp": to_int(
            stats.get("최대 생명력")
        )
    }

def parse_bracelet(equipment):
    bracelet = next(
        (
            item
            for item in equipment
            if item.get("Type") == "팔찌"
        ),
        None
    )

    if not bracelet:
        return None

    raw_tooltip = bracelet.get("Tooltip")

    if not raw_tooltip:
        return None

    try:
        tooltip = json.loads(raw_tooltip)

    except (json.JSONDecodeError, TypeError):
        return None

    # ==============================
    # 티어
    # ==============================

    item_tier = None

    item_title = (
        tooltip
        .get("Element_001", {})
        .get("value", {})
    )

    if isinstance(item_title, dict):

        title_texts = extract_tooltip_text(
            item_title
        )

        for text in title_texts:

            tier_match = re.search(
                r"아이템 티어\s*(\d+)",
                text
            )

            if tier_match:
                item_tier = int(
                    tier_match.group(1)
                )

    # ==============================
    # 팔찌 효과
    # ==============================

    stats = {}
    special_effects = []

    bracelet_effect = (
        tooltip
        .get("Element_005", {})
        .get("value", {})
    )

    if isinstance(bracelet_effect, dict):

        effect_html = bracelet_effect.get(
            "Element_001",
            ""
        )

        # <br> 기준으로 옵션을 분리
        effect_lines = split_tooltip_lines(
            effect_html
        )

        # 능력치로 취급할 항목
        stat_names = [
            "힘",
            "민첩",
            "지능",
            "체력",
            "치명",
            "특화",
            "신속"
        ]

        for line in effect_lines:

            remaining_text = line

            # --------------------------
            # 기본 능력치 추출
            # --------------------------

            for stat_name in stat_names:

                stat_matches = re.findall(
                    rf"{stat_name}\s*\+(\d+)",
                    line
                )

                if stat_matches:

                    stats[stat_name] = int(
                        stat_matches[0]
                    )

                    remaining_text = re.sub(
                        rf"{stat_name}\s*\+\d+",
                        "",
                        remaining_text
                    )

            remaining_text = (
                remaining_text.strip()
            )

            # 기본 능력치를 제거하고
            # 남은 문장은 특수 효과로 저장
            if remaining_text:

                special_effects.append(
                    remaining_text
                )

    # ==============================
    # 도약 포인트
    # ==============================

    leap_point = None

    ark_passive_effect = (
        tooltip
        .get("Element_007", {})
        .get("value", {})
    )

    if isinstance(
        ark_passive_effect,
        dict
    ):

        ark_text = ark_passive_effect.get(
            "Element_001",
            ""
        )

        ark_text = clean_html_text(
            ark_text
        )

        leap_match = re.search(
            r"도약\s*\+(\d+)",
            ark_text
        )

        if leap_match:

            leap_point = int(
                leap_match.group(1)
            )

    return {
        "name": bracelet.get("Name"),
        "icon": bracelet.get("Icon"),
        "grade": bracelet.get("Grade"),
        "item_tier": item_tier,

        "stats": stats,

        "special_effects": special_effects,

        "leap_point": leap_point
    }


    if not profile:
        return None

    stats = {
        stat["Type"]: stat["Value"]
        for stat in profile.get("Stats", [])
    }

    return {
        "character_name": profile.get("CharacterName"),
        "server_name": profile.get("ServerName"),
        "class_name": profile.get("CharacterClassName"),
        "character_level": profile.get("CharacterLevel"),

        "item_level": profile.get("ItemAvgLevel"),
        "combat_power": profile.get("CombatPower"),

        "crit": stats.get("치명"),
        "specialization": stats.get("특화"),
        "swiftness": stats.get("신속"),

        "attack_power": stats.get("공격력"),
        "max_hp": stats.get("최대 생명력")
    }

def parse_character(data):
    if not data:
        return None

    profile = data.get("ArmoryProfile")
    equipment = data.get("ArmoryEquipment", [])

    skill_gem_data = data.get("ArmoryGem")
    engraving_data = data.get("ArmoryEngraving")
    ark_passive_data = data.get("ArkPassive")
    arkgrid_data = data.get("ArkGrid")
    card_data = data.get("ArmoryCard")

    return {
        "profile": parse_profile(
            profile
        ),

        "weapon": parse_weapon(
            equipment
        ),

        "armor": parse_armor(
            equipment
        ),

        "wristguard": parse_wristguard(
            equipment
        ),

        "skill_gems": parse_skill_gems(
            skill_gem_data
        ),

        "engravings": parse_engravings(
            engraving_data
        ),

        "ark_passive": parse_ark_passive(
            ark_passive_data
        ),

        "ark_grid": parse_arkgrid(
            arkgrid_data
        ),

        "cards": parse_cards(
            card_data
        ),

        "accessories": parse_accessories(
            equipment
        ),

        "ability_stone": parse_ability_stone(
            equipment
        ),

        "bracelet": parse_bracelet(
            equipment
        )
    }

def save_processed_character(
    parsed_character,
    output_dir="data/processed"
):
    if not parsed_character:
        return None

    character_name = (
        parsed_character
        .get("profile", {})
        .get("character_name")
    )

    if not character_name:
        return None

    # 저장 폴더 생성
    output_path = Path(output_dir)

    output_path.mkdir(
        parents=True,
        exist_ok=True
    )

    # 파일 경로 생성
    file_path = (
        output_path
        / f"{character_name}.json"
    )

    # JSON 저장
    with open(
        file_path,
        "w",
        encoding="utf-8"
    ) as file:

        json.dump(
            parsed_character,
            file,
            ensure_ascii=False,
            indent=4
        )

    return file_path

def to_int(value):
    if value is None:
        return None

    try:
        return int(
            str(value).replace(",", "")
        )
    except (ValueError, TypeError):
        return None

def to_float(value):
    if value is None:
        return None

    try:
        return float(
            str(value).replace(",", "")
        )
    except (ValueError, TypeError):
        return None

def main():
    json_files = list(Path("data/raw").glob("*.json"))

    if not json_files:
        print("raw JSON 파일이 없습니다.")
        return

    file_path = json_files[0]

    with open(file_path, "r", encoding="utf-8") as file:
        data = json.load(file)

    parsed_character = parse_character(data)
    saved_path = save_processed_character(parsed_character)

    print(f"저장 완료: {saved_path}")

if __name__ == "__main__":
    main()


