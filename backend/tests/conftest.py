import pytest
from sqlalchemy import create_engine, text
from sqlalchemy.exc import OperationalError
from sqlalchemy.orm import Session

from nsa.models import metadata
from nsa.platform.core.db import database_url


@pytest.fixture(scope="session")
def engine():
    eng = create_engine(database_url())
    try:
        with eng.connect() as c:
            c.execute(text("select 1"))
    except OperationalError:
        pytest.skip("PostgreSQL not reachable (set NSA_DATABASE_URL)")
    metadata.create_all(eng)
    yield eng


@pytest.fixture
def session(engine):
    conn = engine.connect()
    tx = conn.begin()
    s = Session(bind=conn, join_transaction_mode="create_savepoint")
    yield s
    s.close()
    tx.rollback()
    conn.close()
