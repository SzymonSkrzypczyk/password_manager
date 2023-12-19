from pathlib import Path
from sqlite3 import Connection, OperationalError
import pytest

from src.db import DBControl, Password

TEMP_PATH = Path(__file__).parent / 'temp.db'
db = None


def setup_module(_module):
    global db
    db = DBControl(TEMP_PATH)


def test_db_get_con():
    con = db.get_con()
    assert isinstance(con, Connection)
    con.close()


def test_raises_error_when_called():
    with pytest.raises(OperationalError):
        db.setup()


def test_db_setup_successful():
    con = db.get_con()

    with con:
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user';")
        data = cur.fetchall()
        assert data is not None
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='passwords';")
        data = cur.fetchall()
        assert data is not None


def test_password_class():
    password = Password(1, "test", "test")
    assert password.name == "test"
    assert password.password == "test"
    assert password.pk == 1


def test_add_user():
    db.add_user("test")
    con = db.get_con()
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM user;")
        data = cur.fetchall()
        assert len(data) == 1
        assert data[0][1] == "test"


def test_add_password():
    db.add_password("test", "test", 0)
    con = db.get_con()
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM passwords;")
        data = cur.fetchall()
        assert len(data) == 1
        assert data[0][1] == "test"


def test_check_user_exists():
    assert not db.check_user_id(0)
    assert db.check_user_id(1)


def test_get_passwords_user():
    passwords = db.get_user_passwords(0)
    assert len(passwords) == 1
    assert passwords[0].name == "test"
    assert passwords[0].password == "test"


def test_delete_password():
    db.delete_password(1)
    con = db.get_con()
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM passwords;")
        data = cur.fetchall()
        assert len(data) == 0


def test_clear_passwords_user():
    db.add_password("test2", "test2", 0)
    db.clear_passwords_user(0)
    con = db.get_con()
    with con:
        cur = con.cursor()
        cur.execute("SELECT * FROM passwords;")
        data = cur.fetchall()
        assert len(data) == 0


def test_get_user_passwords():
    db.add_password("test", "test", 0)
    db.add_password("test2", "test2", 0)
    passwords = db.get_user_passwords(0)
    assert len(passwords) == 2
    assert passwords[0].name == "test"
    assert passwords[1].name == "test2"


def test_get_user_id():
    db.add_user("test2")
    assert db.get_user_id("test") == 1
    assert db.get_user_id("test2") == 2


def test_get_all_users():
    users = db.get_all_users()
    assert len(users) == 2
    assert users[0][1] == "test"
    assert users[1][1] == "test2"


def test_delete_user():
    db.delete_user(2)
    assert len(db.get_all_users()) == 1


def test_rename_user():
    db.rename_user(1, "test3")
    assert db.get_user_id("test3") == 1
    assert db.get_user_id("test3") is not None
    assert db.get_user_id("test") is None
    assert "test3" in db.get_all_users()[0]


def test_update_password():
    db.update_password(3, "test4")
    assert db.get_user_passwords(0)[0].password == "test4"


def test_tables_exist():
    assert db.tables_exist()


def teardown_module(_module):
    global db
    TEMP_PATH.unlink()
    db = None
