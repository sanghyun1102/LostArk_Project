from backend.analysis.dataset_builder import (
    build_character_dataset
)


def main():

    dataframe = (
        build_character_dataset()
    )


    print()
    print("=== LoaP 분석 데이터셋 ===")
    print()


    # ==============================
    # 데이터 크기
    # ==============================

    print(
        f"캐릭터 수: "
        f"{len(dataframe)}"
    )

    print(
        f"컬럼 수: "
        f"{len(dataframe.columns)}"
    )


    # ==============================
    # 컬럼 목록
    # ==============================

    print()
    print("=== 컬럼 ===")

    for column in dataframe.columns:
        print(column)


    # ==============================
    # 데이터 일부 출력
    # ==============================

    print()
    print("=== 데이터 미리보기 ===")

    print(
        dataframe.head()
        .to_string(
            index=False
        )
    )


    # ==============================
    # 자료형 확인
    # ==============================

    print()
    print("=== 자료형 ===")

    print(
        dataframe.dtypes
    )


if __name__ == "__main__":
    main()