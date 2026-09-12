import pandas as pd

from backend.analysis.dataset_builder import (
    build_character_dataset
)


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


def get_target_cohort_dataframe(
    character_name
):
    """
    기준 캐릭터와 같은

    클래스
    + 빌드
    + 아이템 레벨 구간

    데이터를 추출한다.
    """

    dataframe = (
        build_character_dataset()
    )

    if dataframe.empty:
        return None


    target_rows = dataframe[
        dataframe["character_name"]
        == character_name
    ]

    if target_rows.empty:
        return None


    target = target_rows.iloc[0]


    cohort = dataframe[
        (
            dataframe["class_name"]
            == target["class_name"]
        )
        &
        (
            dataframe["build_name"]
            == target["build_name"]
        )
        &
        (
            dataframe["level_band"]
            == target["level_band"]
        )
    ].copy()


    return cohort

def get_feature_quality_report(
    character_name
):
    """
    Cohort Feature별 데이터 존재 여부를 확인한다.
    """

    cohort = get_target_cohort_dataframe(
        character_name
    )

    if (
        cohort is None
        or cohort.empty
    ):
        return None


    total_count = len(cohort)

    rows = []


    for feature in ANALYSIS_FEATURES:

        if feature not in cohort.columns:
            continue


        valid_count = (
            cohort[feature]
            .notna()
            .sum()
        )

        missing_count = (
            total_count
            - valid_count
        )

        missing_rate = round(
            (
                missing_count
                / total_count
            )
            * 100,
            2
        )


        rows.append({
            "feature":
                feature,

            "valid_count":
                valid_count,

            "missing_count":
                missing_count,

            "missing_rate":
                missing_rate
        })


    return {
        "cohort":
            cohort,

        "quality":
            rows
    }

def get_descriptive_statistics(
    character_name
):
    """
    기준 캐릭터 Cohort의
    Feature별 기술 통계를 계산한다.
    """

    cohort = get_target_cohort_dataframe(
        character_name
    )

    if (
        cohort is None
        or cohort.empty
    ):
        return None


    # ==============================
    # 실제 존재하는 Feature만 선택
    # ==============================

    available_features = [
        feature
        for feature in ANALYSIS_FEATURES
        if feature in cohort.columns
    ]


    analysis_data = (
        cohort[
            available_features
        ]
        .copy()
    )


    # ==============================
    # 숫자형으로 변환
    # ==============================

    for column in analysis_data.columns:

        analysis_data[column] = (
            pd.to_numeric(
                analysis_data[column],
                errors="coerce"
            )
        )


    # ==============================
    # 기술 통계
    # ==============================

    statistics = (
        analysis_data
        .describe()
        .T
        .reset_index()
        .rename(
            columns={
                "index": "feature",
                "count": "valid_count",
                "std": "std",
                "25%": "q1",
                "50%": "median",
                "75%": "q3"
            }
        )
    )


    # ==============================
    # 결측치 정보 추가
    # ==============================

    total_count = len(cohort)


    statistics["missing_count"] = (
        total_count
        - statistics["valid_count"]
    )


    statistics["missing_rate"] = (
        (
            statistics["missing_count"]
            / total_count
        )
        * 100
    )


    # ==============================
    # 보기 좋게 반올림
    # ==============================

    numeric_columns = [
        "valid_count",
        "mean",
        "std",
        "min",
        "q1",
        "median",
        "q3",
        "max",
        "missing_count",
        "missing_rate"
    ]


    statistics[
        numeric_columns
    ] = statistics[
        numeric_columns
    ].round(2)


    return statistics

def get_feature_correlations(
    character_name
):
    """
    Cohort의 Feature 간 상관계수를 계산한다.
    """

    cohort = get_target_cohort_dataframe(
        character_name
    )

    if (
        cohort is None
        or cohort.empty
    ):
        return None


    available_features = [
        feature
        for feature in ANALYSIS_FEATURES
        if feature in cohort.columns
    ]


    analysis_data = (
        cohort[
            available_features
        ]
        .copy()
    )


    # 숫자형 변환
    for column in analysis_data.columns:

        analysis_data[column] = (
            pd.to_numeric(
                analysis_data[column],
                errors="coerce"
            )
        )


    # 값이 모두 동일한 Feature 제거
    usable_features = [
        column
        for column in analysis_data.columns
        if analysis_data[column].nunique(
            dropna=True
        ) > 1
    ]


    analysis_data = analysis_data[
        usable_features
    ]


    correlation_matrix = (
        analysis_data
        .corr()
        .round(3)
    )


    return correlation_matrix

def get_combat_power_correlations(
    character_name
):
    """
    동일 Cohort에서 각 Feature와
    전투력의 상관관계를 확인한다.

    보석 미장착 캐릭터는
    조회 시점의 전투력이 크게 왜곡될 수 있으므로
    분석에서 제외한다.
    """

    cohort = get_target_cohort_dataframe(
        character_name
    )

    if (
        cohort is None
        or cohort.empty
    ):
        return None


    # ==============================
    # 보석 정상 장착 캐릭터만 사용
    # ==============================

    valid_cohort = cohort[
        cohort["gem_count"] > 0
    ].copy()


    if valid_cohort.empty:
        return None


    available_features = [
        feature
        for feature in ANALYSIS_FEATURES
        if feature in valid_cohort.columns
    ]


    columns = [
        "combat_power"
    ] + available_features


    analysis_data = (
        valid_cohort[
            columns
        ]
        .copy()
    )


    # ==============================
    # 숫자형 변환
    # ==============================

    for column in analysis_data.columns:

        analysis_data[column] = (
            pd.to_numeric(
                analysis_data[column],
                errors="coerce"
            )
        )


    # ==============================
    # Feature별 전투력 상관관계
    # ==============================

    results = []


    for feature in available_features:

        valid_data = (
            analysis_data[
                [
                    feature,
                    "combat_power"
                ]
            ]
            .dropna()
        )


        if len(valid_data) < 2:
            continue


        # 값이 모두 동일한 Feature 제외
        if (
            valid_data[feature]
            .nunique()
            <= 1
        ):
            continue


        correlation = (
            valid_data[
                feature
            ]
            .corr(
                valid_data[
                    "combat_power"
                ]
            )
        )


        results.append({
            "feature":
                feature,

            "sample_count":
                len(valid_data),

            "combat_power_correlation":
                round(
                    correlation,
                    3
                )
        })


    result_dataframe = (
        pd.DataFrame(
            results
        )
        .sort_values(
            by="combat_power_correlation",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )


    return result_dataframe





