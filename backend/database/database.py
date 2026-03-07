from sqlalchemy.orm import declarative_base, sessionmaker
from sqlmodel import create_engine


SQLITE_URL = "sqlite:///./kane.db"

engine = create_engine(
    SQLITE_URL,
    connect_args={"check_same_thread": False},
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
