from pathlib import Path

from sqlalchemy import create_engine, text
from sqlalchemy.orm import DeclarativeBase, sessionmaker


# ==============================
# DB 파일 경로
# ==============================

BASE_DIR = Path(__file__).resolve().parent.parent.parent

DATA_DIR = BASE_DIR / "data"

DATA_DIR.mkdir(
    parents=True,
    exist_ok=True
)

DB_PATH = DATA_DIR / "loap.db"


# ==============================
# SQLite 연결 주소
# ==============================

DATABASE_URL = (
    f"sqlite:///{DB_PATH.as_posix()}"
)


# ==============================
# SQLAlchemy Engine
# ==============================

engine = create_engine(
    DATABASE_URL,
    connect_args={
        "check_same_thread": False
    }
)


# ==============================
# DB Session
# ==============================

SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False
)


# ==============================
# Model Base Class
# ==============================

class Base(DeclarativeBase):
    pass


# ==============================
# 연결 테스트
# ==============================

def test_connection():

    with engine.connect() as connection:

        connection.execute(
            text("SELECT 1")
        )

    print("DB 연결 성공")
    print(f"DB 위치: {DB_PATH}")

def create_tables():

    # models.py가 로드되어야
    # SQLAlchemy가 테이블 정보를 알 수 있음
    import backend.db.models

    Base.metadata.create_all(
        bind=engine
    )

    print("DB 테이블 생성 완료")

if __name__ == "__main__":

    test_connection()

    create_tables()