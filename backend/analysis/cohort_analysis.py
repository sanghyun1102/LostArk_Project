from backend.analysis.dataset_builder import (
    build_character_dataset
)


def get_cohort_counts():
    """
    클래스 + 빌드 + 아이템 레벨 구간별
    캐릭터 수를 집계한다.
    """

    dataframe = build_character_dataset()

    if dataframe.empty:
        return dataframe

    cohort_counts = (
        dataframe
        .groupby(
            [
                "class_name",
                "build_name",
                "level_band"
            ],
            dropna=False
        )
        .size()
        .reset_index(
            name="character_count"
        )
        .sort_values(
            by="character_count",
            ascending=False
        )
        .reset_index(
            drop=True
        )
    )

    return cohort_counts