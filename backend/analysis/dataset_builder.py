import pandas as pd

from sqlalchemy import select

from backend.db.database import SessionLocal
from backend.db.models import Character

from backend.services.comparison_service import (
    get_build_name,
    get_latest_snapshot
)

from backend.services.feature_service import (
    extract_growth_features
)

from backend.utils.item_level_utils import (
    get_item_level_band
)


def build_character_dataset():
    """
    DB에 저장된 각 캐릭터의 최신 Snapshot을 이용해
    Pandas DataFrame을 생성한다.
    """

    rows = []


    with SessionLocal() as db:

        # ==============================
        # 전체 캐릭터 조회
        # ==============================

        characters = db.scalars(
            select(Character)
        ).all()


        for character in characters:

            # ==============================
            # 최신 Snapshot
            # ==============================

            snapshot = get_latest_snapshot(
                db,
                character.id
            )

            if snapshot is None:
                continue


            processed_data = (
                snapshot.processed_data
                or {}
            )


            # ==============================
            # Feature 추출
            # ==============================

            features = extract_growth_features(
                processed_data
            )


            # ==============================
            # 빌드
            # ==============================

            build_name = get_build_name(
                snapshot
            )


            # ==============================
            # 아이템 레벨 구간
            # ==============================

            item_level = features.get(
                "item_level"
            )

            level_band = get_item_level_band(
                item_level
            )

            if level_band:

                level_band_name = (
                    f"{level_band['start']}"
                    f"-"
                    f"{level_band['display_end']}"
                )

            else:

                level_band_name = None


            # ==============================
            # 기본 정보
            # ==============================

            row = {
                "character_name":
                    character.character_name,

                "server_name":
                    character.server_name,

                "class_name":
                    character.class_name,

                "build_name":
                    build_name,

                "level_band":
                    level_band_name
            }


            # ==============================
            # Feature 합치기
            # ==============================

            row.update(
                features
            )

            rows.append(
                row
            )


    # ==============================
    # DataFrame 생성
    # ==============================

    dataframe = pd.DataFrame(
        rows
    )

    return dataframe