import pytest
from app.database import get_db, SessionLocal


def test_get_db_yields_and_closes():
    gen = get_db()
    db = next(gen)  # triggers yield
    assert db is not None
    with pytest.raises(StopIteration):
        next(gen)  # triggers finally block
