from pathlib import Path
from uuid import uuid4

import pytest
from alembic import command
from alembic.config import Config
from fastapi.testclient import TestClient
from sqlalchemy import create_engine, text
from sqlalchemy.orm import Session

from app.config import get_settings
from app.db import get_db, get_engine
from app.main import app


@pytest.fixture(scope="session")
def test_engine():
    # Dedicated temporary schema; never create/drop tables in public or legacy DBs.
    schema = "auth_test_" + uuid4().hex
    admin = get_engine()
    with admin.begin() as connection:
        connection.execute(text(f'CREATE SCHEMA "{schema}"'))
    engine = create_engine(
        get_settings().database_url.get_secret_value(),
        connect_args={"options": f"-csearch_path={schema}"},
        hide_parameters=True,
    )
    config = Config(str(Path(__file__).resolve().parents[1] / "alembic.ini"))
    try:
        with engine.begin() as connection:
            config.attributes["connection"] = connection
            command.upgrade(config, "head")
        yield engine
        with engine.begin() as connection:
            config.attributes["connection"] = connection
            command.downgrade(config, "base")
            count = connection.scalar(text(
                "SELECT count(*) FROM information_schema.tables "
                "WHERE table_schema = :schema AND table_name <> 'alembic_version'"
            ), {"schema": schema})
            assert count == 0
    finally:
        engine.dispose()
        with admin.begin() as connection:
            connection.execute(text(f'DROP SCHEMA "{schema}" CASCADE'))


@pytest.fixture
def db(test_engine):
    with test_engine.connect() as connection:
        transaction = connection.begin()
        with Session(bind=connection, join_transaction_mode="create_savepoint") as session:
            yield session
        transaction.rollback()


@pytest.fixture
def client(db):
    def override_db():
        yield db

    app.dependency_overrides[get_db] = override_db
    try:
        with TestClient(app) as client:
            yield client
    finally:
        app.dependency_overrides.clear()
