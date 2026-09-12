from statistics import mean, median

from sqlalchemy import select

from backend.db.database import SessionLocal
from backend.db.models import (
    Character,
    CharacterSnapshot
)

from backend.services.comparison_service import (
    get_comparison_cohort,
    get_latest_snapshot
)

from backend.services.feature_service import (
    extract_growth_features
)


# ==============================
# 우선 분석할 Feature
# ==============================

ANALYSIS_FEATURES = [
    "weapon_enhancement",
    "weapon_quality",

    "armor_avg_enhancement",
    "armor_avg_quality",

    "gem_avg_level",
    "damage_gem_avg_level",
    "cooldown_gem_avg_level",

    "card_total_awake",

    "accessory_avg_quality",

    "ark_grid_total_point"
]


def calculate_percentile(
    target_value,
    values
):
    """
    target_value 이하의 값이
    전체에서 차지하는 비율을 계산한다.
    """

    if (
        target_value is None
        or not values
    ):
        return None

    lower_or_equal_count = sum(
        1
        for value in values
        if value <= target_value
    )

    return round(
        (
            lower_or_equal_count
            / len(values)
        )
        * 100,
        2
    )


def calculate_feature_statistics(
    target_value,
    values
):
    """
    하나의 Feature에 대해
    기본 통계와 백분위를 계산한다.
    """

    valid_values = [
        value
        for value in values
        if value is not None
    ]

    if (
        target_value is None
        or not valid_values
    ):
        return None

    return {
        "target":
            target_value,

        "mean":
            round(
                mean(valid_values),
                2
            ),

        "median":
            round(
                median(valid_values),
                2
            ),

        "min":
            min(valid_values),

        "max":
            max(valid_values),

        "percentile":
            calculate_percentile(
                target_value,
                valid_values
            ),

        "sample_count":
            len(valid_values)
    }


def get_feature_analysis(
    character_name
):
    """
    기준 캐릭터와 동일 Cohort의
    성장 요소별 통계를 계산한다.
    """

    cohort_result = get_comparison_cohort(
        character_name
    )


    if (
        cohort_result.get("status")
        != "ok"
    ):
        return cohort_result


    target_info = cohort_result.get(
        "target",
        {}
    )

    cohort_characters = (
        cohort_result.get(
            "characters",
            []
        )
    )


    with SessionLocal() as db:

        # ==============================
        # 기준 캐릭터
        # ==============================

        target_character = db.scalar(
            select(Character)
            .where(
                Character.character_name
                == character_name
            )
        )

        if target_character is None:

            return {
                "status":
                    "character_not_found"
            }


        target_snapshot = (
            get_latest_snapshot(
                db,
                target_character.id
            )
        )

        if target_snapshot is None:

            return {
                "status":
                    "snapshot_not_found"
            }


        target_features = (
            extract_growth_features(
                target_snapshot.processed_data
            )
        )


        # ==============================
        # Cohort 전체 Feature
        # 기준 캐릭터 자신도 포함
        # ==============================

        all_features = [
            target_features
        ]


        for cohort_character in (
            cohort_characters
        ):

            cohort_name = (
                cohort_character.get(
                    "character_name"
                )
            )


            character = db.scalar(
                select(Character)
                .where(
                    Character.character_name
                    == cohort_name
                )
            )

            if character is None:
                continue


            snapshot = get_latest_snapshot(
                db,
                character.id
            )

            if snapshot is None:
                continue


            features = (
                extract_growth_features(
                    snapshot.processed_data
                )
            )

            all_features.append(
                features
            )


        # ==============================
        # Feature별 통계 계산
        # ==============================

        analysis = {}


        for feature_name in (
            ANALYSIS_FEATURES
        ):

            target_value = (
                target_features.get(
                    feature_name
                )
            )

            values = [
                features.get(
                    feature_name
                )
                for features in all_features
            ]


            analysis[
                feature_name
            ] = (
                calculate_feature_statistics(
                    target_value,
                    values
                )
            )


        return {
            "status":
                "ok",

            "target":
                target_info,

            "criteria":
                cohort_result.get(
                    "criteria"
                ),

            "cohort_size":
                len(all_features),

            "features":
                analysis
        }