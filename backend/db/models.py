from datetime import datetime

from sqlalchemy import (
    DateTime,
    Float,
    ForeignKey,
    Integer,
    JSON,
    String
)

from sqlalchemy.orm import (
    Mapped,
    mapped_column,
    relationship
)

from backend.db.database import Base


# ==============================
# Character
# ==============================

class Character(Base):

    __tablename__ = "characters"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    character_name: Mapped[str] = mapped_column(
        String(50),
        unique=True,
        nullable=False,
        index=True
    )

    server_name: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    class_name: Mapped[str | None] = mapped_column(
        String(30),
        nullable=True
    )

    snapshots: Mapped[list["CharacterSnapshot"]] = relationship(
        back_populates="character",
        cascade="all, delete-orphan"
    )


# ==============================
# Character Snapshot
# ==============================

class CharacterSnapshot(Base):

    __tablename__ = "character_snapshots"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        autoincrement=True
    )

    character_id: Mapped[int] = mapped_column(
        ForeignKey("characters.id"),
        nullable=False,
        index=True
    )

    captured_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.now,
        nullable=False,
        index=True
    )

    # ==============================
    # 기본 스펙
    # ==============================

    item_level: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    combat_power: Mapped[float | None] = mapped_column(
        Float,
        nullable=True
    )

    attack_power: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    max_hp: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    crit: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    specialization: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    swiftness: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    # ==============================
    # 무기
    # ==============================

    weapon_enhancement: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    weapon_item_level: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    weapon_quality: Mapped[int | None] = mapped_column(
        Integer,
        nullable=True
    )

    # ==============================
    # 전체 processed JSON
    # ==============================

    processed_data: Mapped[dict | None] = mapped_column(
        JSON,
        nullable=True
    )

    # ==============================
    # Relationship
    # ==============================

    character: Mapped["Character"] = relationship(
        back_populates="snapshots"
    )