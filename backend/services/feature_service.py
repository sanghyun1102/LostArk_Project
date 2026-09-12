import re

def safe_average(values):
    """
    None을 제외한 숫자들의 평균을 계산한다.
    """

    valid_values = [
        value
        for value in values
        if value is not None
    ]

    if not valid_values:
        return None

    return round(
        sum(valid_values)
        / len(valid_values),
        2
    )


def extract_growth_features(
    processed_data
):
    """
    processed_data에서
    스펙 비교에 사용할 숫자형 Feature를 추출한다.

    아직 점수화는 하지 않는다.
    """

    if not processed_data:
        return {}


    # ==============================
    # Profile
    # ==============================

    profile = (
        processed_data.get("profile")
        or {}
    )


    # ==============================
    # Weapon
    # ==============================

    weapon = (
        processed_data.get("weapon")
        or {}
    )


    # ==============================
    # Armor
    # ==============================

    armor = (
        processed_data.get("armor")
        or []
    )

    armor_enhancements = [
        item.get("enhancement_level")
        for item in armor
    ]

    armor_qualities = [
        item.get("quality")
        for item in armor
    ]


    # ==============================
    # Skill Gems
    # ==============================

    skill_gem_data = (
        processed_data.get("skill_gems")
        or {}
    )

    gems = (
        skill_gem_data.get("gems")
        or []
    )

    gem_levels = [
        gem.get("level")
        for gem in gems
        if gem.get("level") is not None
    ]

    damage_gems = []
    cooldown_gems = []

    damage_effects = []
    cooldown_effects = []


    for gem in gems:

        effect_descriptions = (
            gem.get("effect_description")
            or []
        )


        for description in effect_descriptions:

            # ==============================
            # 피해 증가 보석
            # ==============================

            if "피해" in description:

                damage_gems.append(
                    gem
                )

                percentage = (
                    extract_percentage(
                        description
                    )
                )

                if percentage is not None:

                    damage_effects.append(
                        percentage
                    )

                break


            # ==============================
            # 재사용 대기시간 감소 보석
            # ==============================

            if (
                "재사용 대기시간"
                in description
            ):

                cooldown_gems.append(
                    gem
                )

                percentage = (
                    extract_percentage(
                        description
                    )
                )

                if percentage is not None:

                    cooldown_effects.append(
                        percentage
                    )

                break

    brilliance_gems = [
        gem
        for gem in gems
        if gem.get("type") == "광휘"
    ]


    # ==============================
    # Cards
    # ==============================

    cards = (
        processed_data.get("cards")
        or {}
    )


    # ==============================
    # Accessories
    # ==============================

    accessories = (
        processed_data.get("accessories")
        or []
    )

    accessory_qualities = [
        item.get("quality")
        for item in accessories
    ]


    # ==============================
    # ArkGrid
    # ==============================

    ark_grid = (
        processed_data.get("ark_grid")
        or {}
    )

    ark_grid_cores = (
        ark_grid.get("cores")
        or []
    )

    ark_grid_points = [
        core.get("point")
        for core in ark_grid_cores
        if core.get("point") is not None
    ]


    # ==============================
    # Feature 반환
    # ==============================

    return {
        # 기본 정보
        "item_level":
            profile.get("item_level"),

        "combat_power":
            profile.get("combat_power"),


        # 무기
        "weapon_enhancement":
            weapon.get("enhancement_level"),

        "weapon_item_level":
            weapon.get("item_level"),

        "weapon_quality":
            weapon.get("quality"),


        # 방어구
        "armor_avg_enhancement":
            safe_average(
                armor_enhancements
            ),

        "armor_avg_quality":
            safe_average(
                armor_qualities
            ),


        # 보석
        "gem_count":
            len(gems),

        "gem_avg_level":
            safe_average(
                gem_levels
            ),

        "damage_gem_count":
            len(damage_gems),

        "damage_gem_avg_level":
            safe_average([
                gem.get("level")
                for gem in damage_gems
            ]),

        "cooldown_gem_count":
            len(cooldown_gems),

        "cooldown_gem_avg_level":
            safe_average([
                gem.get("level")
                for gem in cooldown_gems
            ]),

        "damage_gem_avg_effect":
            safe_average(
                damage_effects
            ),

        "cooldown_gem_avg_effect":
            safe_average(
                cooldown_effects
            ),

        "brilliance_gem_count":
            len(brilliance_gems),

        "brilliance_gem_avg_level":
            safe_average([
                gem.get("level")
                for gem in brilliance_gems
            ]),


        # 카드
        "card_total_awake":
            cards.get("total_awake"),


        # 액세서리
        "accessory_avg_quality":
            safe_average(
                accessory_qualities
            ),


        # 아크그리드
        "ark_grid_core_count":
            len(ark_grid_cores),

        "ark_grid_total_point":
            (
                sum(ark_grid_points)
                if ark_grid_points
                else None
            )
    }


def extract_percentage(text):
    """
    문자열에서 첫 번째 퍼센트 값을 추출한다.

    예:
    '피해 40.00% 증가'
    → 40.0
    """

    if not isinstance(text, str):
        return None

    match = re.search(
        r"(\d+(?:\.\d+)?)%",
        text
    )

    if not match:
        return None

    return float(
        match.group(1)
    )