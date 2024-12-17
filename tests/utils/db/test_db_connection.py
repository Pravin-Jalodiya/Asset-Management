from src.app.utils.db.db import DB


def test_db_connection():
    conn = DB.get_connection()

    assert conn is not None