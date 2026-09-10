from pathlib import Path

from backend.collectors.collect_character import collect_character
from backend.services.snapshot_service import save_character_snapshot


BASE_DIR = Path(__file__).resolve().parent.parent

SEED_FILE = (
    BASE_DIR
    / "data"
    / "seeds"
    / "character_names.txt"
)


def load_character_names():
    """
    character_names.txt에서
    캐릭터 이름 목록을 읽는다.
    """

    if not SEED_FILE.exists():
        print(
            f"캐릭터 목록 파일이 없습니다: "
            f"{SEED_FILE}"
        )

        return []

    with open(
        SEED_FILE,
        "r",
        encoding="utf-8"
    ) as file:

        names = [
            line.strip()
            for line in file
            if line.strip()
        ]

    # 중복 제거
    return list(
        dict.fromkeys(names)
    )


def batch_collect():
    """
    여러 캐릭터를 순서대로 수집하고
    DB Snapshot까지 저장한다.
    """

    character_names = (
        load_character_names()
    )

    if not character_names:
        print(
            "수집할 캐릭터가 없습니다."
        )
        return


    success_count = 0
    fail_count = 0


    print()
    print(
        f"총 {len(character_names)}명 "
        f"수집 시작"
    )
    print("=" * 40)


    for index, character_name in enumerate(
        character_names,
        start=1
    ):

        print()
        print(
            f"[{index}/{len(character_names)}] "
            f"{character_name}"
        )


        try:

            character_data = (
                collect_character(
                    character_name
                )
            )

            if not character_data:

                print(
                    f"수집 실패: "
                    f"{character_name}"
                )

                fail_count += 1
                continue


            save_character_snapshot(
                character_data
            )

            success_count += 1


        except Exception as error:

            print(
                f"오류 발생: "
                f"{character_name}"
            )

            print(
                f"{type(error).__name__}: "
                f"{error}"
            )

            fail_count += 1

            # 한 캐릭터가 실패해도
            # 다음 캐릭터 계속 진행
            continue


    print()
    print("=" * 40)

    print(
        f"수집 완료"
    )

    print(
        f"성공: {success_count}명"
    )

    print(
        f"실패: {fail_count}명"
    )


if __name__ == "__main__":
    batch_collect()