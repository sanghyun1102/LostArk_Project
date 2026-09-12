from statistics import mean, median

from backend.services.comparison_service import (
    get_comparison_cohort
)


def round_value(
    value,
    digits=2
):
    """
    숫자를 지정한 소수점 자리까지 반올림한다.
    """

    if value is None:
        return None

    return round(
        value,
        digits
    )


def get_cohort_statistics(
    character_name
):
    """
    최종 Cohort의 기본 통계를 계산한다.

    현재 분석 항목:
    - 아이템 레벨
    - 전투력
    """

    cohort_result = get_comparison_cohort(
        character_name
    )


    # ==============================
    # Cohort 조회 실패
    # ==============================

    if (
        cohort_result.get("status")
        != "ok"
    ):

        return cohort_result


    target = cohort_result.get(
        "target",
        {}
    )

    comparison_characters = (
        cohort_result.get(
            "characters",
            []
        )
    )


    # ==============================
    # 비교 대상 값 추출
    # ==============================

    item_levels = [
        character["item_level"]
        for character in comparison_characters
        if character.get("item_level")
        is not None
    ]

    combat_powers = [
        character["combat_power"]
        for character in comparison_characters
        if character.get("combat_power")
        is not None
    ]


    # ==============================
    # 데이터 부족 여부
    # ==============================

    if not comparison_characters:

        return {
            "status":
                "insufficient_data",

            "target":
                target,

            "criteria":
                cohort_result.get(
                    "criteria"
                ),

            "comparison_count":
                0,

            "message":
                "비교 가능한 Cohort 데이터가 없습니다."
        }


    # ==============================
    # 아이템 레벨 통계
    # ==============================

    item_level_statistics = None

    if item_levels:

        item_level_statistics = {
            "mean":
                round_value(
                    mean(item_levels)
                ),

            "median":
                round_value(
                    median(item_levels)
                ),

            "min":
                round_value(
                    min(item_levels)
                ),

            "max":
                round_value(
                    max(item_levels)
                )
        }


    # ==============================
    # 전투력 통계
    # ==============================

    combat_power_statistics = None

    if combat_powers:

        combat_power_statistics = {
            "mean":
                round_value(
                    mean(combat_powers)
                ),

            "median":
                round_value(
                    median(combat_powers)
                ),

            "min":
                round_value(
                    min(combat_powers)
                ),

            "max":
                round_value(
                    max(combat_powers)
                )
        }


    # ==============================
    # 결과
    # ==============================

    return {
        "status":
            "ok",

        "target":
            target,

        "criteria":
            cohort_result.get(
                "criteria"
            ),

        "comparison_count":
            len(
                comparison_characters
            ),

        "statistics": {

            "item_level":
                item_level_statistics,

            "combat_power":
                combat_power_statistics
        }
    }

def get_combat_power_percentile(
    character_name
):
    """
    같은 Cohort 안에서
    기준 캐릭터의 전투력 위치를 계산한다.

    반환:
    - 전체 표본 수
    - 순위
    - 상위 비율
    - 백분위
    """

    cohort_result = get_comparison_cohort(
        character_name
    )

    if (
        cohort_result.get("status")
        != "ok"
    ):
        return cohort_result


    target = cohort_result.get(
        "target",
        {}
    )

    target_combat_power = target.get(
        "combat_power"
    )

    comparison_characters = (
        cohort_result.get(
            "characters",
            []
        )
    )


    if target_combat_power is None:

        return {
            "status":
                "combat_power_not_found",

            "message":
                "기준 캐릭터의 전투력 정보가 없습니다."
        }


    # ==============================
    # Cohort 전투력 목록
    # 기준 캐릭터도 포함
    # ==============================

    combat_powers = [
        character.get(
            "combat_power"
        )
        for character in comparison_characters
        if character.get(
            "combat_power"
        ) is not None
    ]

    combat_powers.append(
        target_combat_power
    )


    total_count = len(
        combat_powers
    )


    # ==============================
    # 데이터 부족
    # ==============================

    if total_count < 2:

        return {
            "status":
                "insufficient_data",

            "target":
                target,

            "sample_count":
                total_count,

            "message":
                "백분위 계산을 위한 "
                "비교 데이터가 부족합니다."
        }


    # ==============================
    # 순위 계산
    #
    # 자신보다 전투력이 높은 사람이
    # 몇 명인지 확인
    # ==============================

    higher_count = sum(
        1
        for combat_power in combat_powers
        if combat_power
        > target_combat_power
    )

    rank = (
        higher_count
        + 1
    )


    # ==============================
    # 상위 비율
    #
    # rank 1 / 10명
    # → 상위 10%
    # ==============================

    top_percentage = round(
        (
            rank
            / total_count
        )
        * 100,
        2
    )


    # ==============================
    # 백분위 계산
    #
    # 자신 이하의 캐릭터가
    # 전체 중 몇 %인지 계산
    # ==============================

    lower_or_equal_count = sum(
        1
        for combat_power in combat_powers
        if combat_power
        <= target_combat_power
    )

    percentile = round(
        (
            lower_or_equal_count
            / total_count
        )
        * 100,
        2
    )


    return {
        "status":
            "ok",

        "target": {
            "character_name":
                target.get(
                    "character_name"
                ),

            "class_name":
                target.get(
                    "class_name"
                ),

            "build_name":
                target.get(
                    "build_name"
                ),

            "item_level":
                target.get(
                    "item_level"
                ),

            "combat_power":
                target_combat_power
        },

        "criteria":
            cohort_result.get(
                "criteria"
            ),

        "sample_count":
            total_count,

        "ranking": {
            "rank":
                rank,

            "top_percentage":
                top_percentage,

            "percentile":
                percentile
        }
    }