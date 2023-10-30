from pathlib import Path
from typing import Union
import sqlite3
from uuid import uuid4
from collections import namedtuple

Password = namedtuple("Password", "pk name password")


class DBControl:
    """
    Probably will be changed to SQLalchemy
    The DB is not safe from injections
    """
    def __init__(self, path: Union[str, Path] = Path(__file__).parent / 'db.sql'):
        self.path = Path(path)
        if not self.path.exists():
            self.setup()

    def get_con(self):
        return sqlite3.connect(str(self.path))

    def setup(self):
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute("""CREATE TABLE user(
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(150) UNIQUE
            );""")
            cur.execute("""CREATE TABLE passwords(
            pk INTEGER PRIMARY KEY AUTOINCREMENT,
            name VARCHAR(255),
            password VARCHAR(100) NOT NULL,
            user_id INTEGER NOT NULL,
            FOREIGN KEY(user_id) REFERENCES user(pk)
            );""")
            con.commit()

    def add_user(self, name: str):
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"INSERT INTO user(name) VALUES('{name}');")
            con.commit()

    def add_password(self, name: str, password: str, user_id: int):
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"INSERT INTO passwords(name, password, user_id) VALUES('{name}', '{password}', {user_id});")
            con.commit()

    def clear_passwords_user(self, user_id: int):
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"DELETE FROM passwords WHERE user_id={user_id};")
            con.commit()

    def delete_password(self, password_id: int):
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"DELETE FROM passwords WHERE pk={password_id};")
            con.commit()

    def get_user_passwords(self, user_id: int):
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM passwords WHERE user_id={user_id};")
            data = [Password(i[0], i[1], i[2]) for i in cur.fetchall()]
        return data

    def get_user_id(self, name: str):
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM user WHERE name='{name}'")
            return cur.fetchone()[0]

    def update_password(self, password_id: int, new_password: str):
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"UPDATE passwords SET password='{new_password}' WHERE pk={password_id};")
            con.commit()


if __name__ == "__main__":
    db = DBControl()
    # db.add_user('XD')
    # db.add_password('DX', 'XDDD', 1)
    print(db.get_user_passwords(1))
    # db.get_user_passwords()
