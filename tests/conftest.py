"""Viseron fixtures."""
from __future__ import annotations

from typing import Any, Generator, Iterator
from unittest.mock import MagicMock, patch

import pytest
from pytest_postgresql import factories
from pytest_postgresql.janitor import DatabaseJanitor
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from viseron import Viseron
from viseron.components.data_stream import COMPONENT as DATA_STREAM, DataStream
from viseron.components.storage.models import Base

from tests.common import MockCamera

test_db = factories.postgresql_proc(port=None, dbname="test_db")


@pytest.fixture
def vis() -> Viseron:
    """Fixture to test Viseron instance."""
    viseron = Viseron()
    viseron.data[DATA_STREAM] = MagicMock(spec=DataStream)
    return viseron


@pytest.fixture
def camera() -> MockCamera:
    """Fixture to test camera."""
    return MockCamera()


@pytest.fixture(scope="session", autouse=True)
def patch_enable_logging() -> Iterator[None]:
    """Patch enable_logging to avoid adding duplicate handlers."""
    with patch("viseron.enable_logging"):
        yield


def _make_db_session(database) -> Generator[Session, Any, None]:
    """Create a DB session."""
    with DatabaseJanitor(
        database.user,
        database.host,
        database.port,
        database.dbname,
        database.version,
        database.password,
    ):
        connection_str = (
            "postgresql+psycopg2://"
            f"{database.user}:@{database.host}:{database.port}/{database.dbname}"
        )
        engine = create_engine(connection_str)
        Base.metadata.create_all(engine)
        _sessionmaker = sessionmaker(bind=engine, expire_on_commit=False)
        with _sessionmaker() as session:
            yield session
        Base.metadata.drop_all(engine)


def _get_db_session(database) -> Generator[sessionmaker[Session], Any, None]:
    """Create a DB session."""
    with DatabaseJanitor(
        database.user,
        database.host,
        database.port,
        database.dbname,
        database.version,
        database.password,
    ):
        connection_str = (
            "postgresql+psycopg2://"
            f"{database.user}:@{database.host}:{database.port}/{database.dbname}"
        )
        engine = create_engine(connection_str)
        Base.metadata.create_all(engine)
        yield sessionmaker(bind=engine, expire_on_commit=False)
        Base.metadata.drop_all(engine)


@pytest.fixture(scope="function")
def db_session(test_db):
    """Session for SQLAlchemy."""
    yield from _make_db_session(test_db)


@pytest.fixture(scope="class")
def db_session_class(test_db):
    """Session for SQLAlchemy."""
    yield from _make_db_session(test_db)


@pytest.fixture(scope="function")
def get_db_session(test_db):
    """Session for SQLAlchemy."""
    yield from _get_db_session(test_db)


@pytest.fixture
def alembic_config() -> dict[str, str]:
    """Return config for pytest-alembic."""
    return {
        "file": "viseron/components/storage/alembic.ini",
        "script_location": "viseron/components/storage/alembic",
    }


@pytest.fixture
def alembic_engine(test_db):
    """Return engine for pytest-alembic."""
    with DatabaseJanitor(
        test_db.user,
        test_db.host,
        test_db.port,
        test_db.dbname,
        test_db.version,
        test_db.password,
    ):
        connection_str = (
            "postgresql+psycopg2://"
            f"{test_db.user}:@{test_db.host}:{test_db.port}/{test_db.dbname}"
        )
        yield create_engine(connection_str)
