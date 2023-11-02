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
            cur.execute(f"INSERT INTO user(name) VALUES('{name}') RETURNING *;")
            index = cur.fetchone()[0] + 1
            con.commit()
        return index

    def check_user_id(self, user_id: int):
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM user;")
            if len([i for i in cur.fetchall() if i[0] == user_id]):
                return True
        return False

    def add_password(self, name: str, password: str, user_id: int):
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"INSERT INTO passwords(name, password, user_id) VALUES('{name}', '{password}',"
                        f" {user_id}) RETURNING *;")
            index = cur.fetchone()[0] + 1
            con.commit()
        return index

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
            data = cur.fetchone()
        if data:
            return data[0]
        else:
            # co robicw takim wypadku?
            return None

    def get_all_users(self):
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM user;")
            data = cur.fetchall()
        return data

    def update_password(self, password_id: int, new_password: str):
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"UPDATE passwords SET password='{new_password}' WHERE pk={password_id};")
            con.commit()


if __name__ == "__main__":
    db = DBControl()
    # db.add_user('XD')
    # db.add_password('DX', 'XDDD', 1)
    print(db.check_user_id(1))
    # print(db.get_user_passwords(1))
    # db.get_user_passwords()
