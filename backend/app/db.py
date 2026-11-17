from functools import lru_cache

from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from collections.abc import Iterator

from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.config import get_settings


class Base(DeclarativeBase):
    pass


@lru_cache
def get_engine() -> Engine:
    return create_engine(
        get_settings().database_url.get_secret_value(),
        pool_pre_ping=True,
        hide_parameters=True,
    )


def get_db() -> Iterator[Session]:
    session_factory = sessionmaker(bind=get_engine())
    with session_factory() as session:
        yield session
