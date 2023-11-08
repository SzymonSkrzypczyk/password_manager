from os import getenv
from pathlib import Path
from typing import Union, List, Tuple
import sqlite3
from collections import namedtuple
from dotenv import load_dotenv

Password = namedtuple("Password", "pk name password")
DEFAULT_DB_PATH = Path(__file__).parent.parent / 'data' / 'db.sql'
load_dotenv(Path(__file__).parent.parent / '.env')
FERNET_KEY = getenv("FERNET_KEY")

"""
dodac klucz Ferneta do usera!
"""


class DBControl:
    """
    A class supposed to be an intermediary between app and database
    In the nearest future will be replaced by SQLAlchemy
    """
    def __init__(self, path: Union[str, Path] = DEFAULT_DB_PATH):
        """Initializes DBControl class, if the specified file does not exist sets up the database structure

        :param path: Path to the database file, if none provided, then uses DEFAULT_DB_PATH
        :type path: Union[str, Path]
        """
        self.path = Path(path)
        if not self.path.exists() or not self.tables_exist():
            self.setup()
        elif self.path.is_dir():
            raise FileNotFoundError("You have to provide a path to a file not directory!") from None

    def get_con(self) -> sqlite3.Connection:
        """Opens and returns connection to the database

        :return: connection object
        :rtype: sqlite3.Connection
        """
        return sqlite3.connect(str(self.path))

    def setup(self) -> None:
        """Sets up tables in the database, if the database file does not already exist

        :return: returns nothing
        :rtype: None
        """
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

    def add_user(self, name: str) -> int:
        """Adds user to the "user" table

        :param name: name of the user
        :type name: str
        :return: Index of the added user
        :rtype: int
        """
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"INSERT INTO user(name) VALUES('{name}') RETURNING *;")
            index = cur.fetchone()[0] + 1
            con.commit()
        return index

    def check_user_id(self, user_id: int) -> bool:
        """Checks whether user exists in "user" table

        :param user_id: Id of the user that we want to look up
        :type user_id: int
        :return: True if user exists, otherwise False
        :rtype: bool
        """
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM user;")
            if len([i for i in cur.fetchall() if i[0] == user_id]):
                return True
        return False

    def add_password(self, name: str, password: str, user_id: int) -> int:
        """Adds password for a given ID of an user

        :param name: name of the website/app that we want to save a password from
        :type name: str
        :param password: the password to the website/app
        :type password: str
        :param user_id: ID of the user
        :type user_id: int
        :return: ID of an added password
        :rtype: int
        """
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"INSERT INTO passwords(name, password, user_id) VALUES('{name}', '{password}',"
                        f" {user_id}) RETURNING *;")
            index = cur.fetchone()[0] + 1
            con.commit()
        return index

    def clear_passwords_user(self, user_id: int) -> None:
        """Deletes all passwords for a given user

        :param user_id: ID of the user
        :type user_id: int
        :return: Nothing
        :rtype: None
        """
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"DELETE FROM passwords WHERE user_id={user_id};")
            con.commit()

    def delete_password(self, password_id: int) -> None:
        """Deletes password of a given ID

        :param password_id: ID of the password
        :type password_id: int
        :return: nothing
        :rtype: None
        """
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"DELETE FROM passwords WHERE pk={password_id};")
            con.commit()

    def get_user_passwords(self, user_id: int) -> List[Password]:
        """Returns passwords of a given user

        :param user_id: ID of the user
        :type user_id: int
        :return: list of passwords
        :rtype: List[Password]
        """
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM passwords WHERE user_id={user_id};")
            data = [Password(i[0], i[1], i[2]) for i in cur.fetchall()]
        return data

    def get_user_id(self, name: str) -> Union[int, None]:
        """Returns ID of an user of a given name

        :param name: name of the user
        :type name: str
        :return: ID of the user or None if such does not exist
        :rtype: Union[int, None]
        """
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM user WHERE name='{name}'")
            data = cur.fetchone()
        if data:
            return data[0]
        else:
            # co robicw takim wypadku?
            return None

    def get_all_users(self) -> List[Tuple]:
        """Returns all users in the user table

        :return: Tuple of all users
        :rtype: List[Tuple]
        """
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"SELECT * FROM user;")
            data = cur.fetchall()
        return data

    def delete_user(self, index: int) -> None:
        """Deletes user of a given ID

        :param index: ID of the user to be deleted
        :type index: int
        :return: nothing
        :rtype: None
        """
        self.delete_password(index)
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"DELETE FROM user WHERE pk={index};")
            con.commit()

    def rename_user(self, index: int, new_name: str) -> None:
        """Renames user of a given ID with a new name

        :param index: ID of the user
        :type index: int
        :param new_name: new name of the user
        :type new_name: str
        :return: nothing
        :rtype: None
        """
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"UPDATE user SET name='{new_name}' WHERE pk={index};")
            con.commit()

    def update_password(self, password_id: int, new_password: str) -> None:
        """Updates password of a given ID

        :param password_id: ID of the password
        :type password_id: int
        :param new_password: a new password to be set
        :type new_password: str
        :return: nothing
        :rtype: None
        """
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute(f"UPDATE passwords SET password='{new_password}' WHERE pk={password_id};")
            con.commit()

    def tables_exist(self) -> bool:
        """Checks whether user table exists

        :return: True if table exists, otherwise False
        :rtype: bool
        """
        with self.get_con() as con:
            cur = con.cursor()
            cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='user';")
            res = len(cur.fetchall())
        return bool(res)


if __name__ == "__main__":
    db = DBControl()
    # db.rename_user(1, 'test')
    print(db.get_all_users())
