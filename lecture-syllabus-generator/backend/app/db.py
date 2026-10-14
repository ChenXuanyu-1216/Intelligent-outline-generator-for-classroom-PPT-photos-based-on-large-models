from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from app.config import settings, DATA_DIR

DATA_DIR.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    settings.database_url,
    connect_args={"check_same_thread": False},
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)
    # Upgrade existing SQLite databases without deleting their records.
    if engine.dialect.name == "sqlite":
        with engine.begin() as connection:
            columns = {column["name"] for column in inspect(connection).get_columns("page")}
            if "recognized_structured" not in columns:
                connection.execute(text("ALTER TABLE page ADD COLUMN recognized_structured JSON"))
