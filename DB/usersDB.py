import sqlite3
import os
import time
from dataclasses import dataclass
from typing import Union, List, Dict, Optional

PHOTOS_DB = f'{os.path.dirname(__file__)}/usersDB.db'
conn_loc = sqlite3.connect(PHOTOS_DB)
cursor_loc = conn_loc.cursor()

cursor_loc.execute('''
    CREATE TABLE IF NOT EXISTS users_info (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        admin BOOL DEFAULT False,
        public_preview BOOL DEFAULT True
    )
''')
cursor_loc.execute('''
    CREATE TABLE IF NOT EXISTS UserQueries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        query TEXT
    )
''')
cursor_loc.close()
conn_loc.close()


@dataclass
class UserQuery:
    user_id: int
    queries: Dict[int, str]


@dataclass
class UserSets:
    user_id: int
    username: str
    admin: bool
    public_preview: bool


def add_user(user_id: int, username: Optional[str] = None):
    try:
        with sqlite3.connect(PHOTOS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users_info (user_id, username) 
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET 
                username = excluded.username
            ''', (user_id, username))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")


def get_users_from_db() -> List['UserSets']:
    with sqlite3.connect(PHOTOS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT * FROM users_info ORDER BY CASE WHEN username IS NULL THEN 1 ELSE 0 END, username ASC"
        )
        rows = cursor.fetchall()
        users = [UserSets(*row) for row in rows]
        return users


def set_admin(user_id: int):
    try:
        add_user(user_id)
        with sqlite3.connect(PHOTOS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users_info SET admin=? WHERE user_id=?",
                           (True, user_id))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")


def set_public_name(user_id: int, show_name: bool = True):
    try:
        add_user(user_id)
        with sqlite3.connect(PHOTOS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users_info SET public_preview=? WHERE user_id=?",
                           (show_name, user_id))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")


def get_user(user_id: Optional[int] = None, username: Optional[str] = None) -> Optional['UserSets']:
    with sqlite3.connect(PHOTOS_DB) as conn:
        cursor = conn.cursor()
        if user_id:
            cursor.execute("SELECT * FROM users_info WHERE user_id=?", (user_id,))
        elif username:
            cursor.execute("SELECT * FROM users_info WHERE username=?", (username,))
        else:
            return None
        row = cursor.fetchone()
        if row is None:
            if user_id:
                add_user(user_id)
                return UserSets(user_id, username, False, True)
            return None
        if username and user_id:
            add_user(user_id, username)
        return UserSets(*row)


def add_user_query(user_id: int, username: str, query: str):
    try:
        add_user(user_id, username)
        with sqlite3.connect(PHOTOS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO UserQueries (user_id, timestamp, query) VALUES (?, ?, ?)",
                           (user_id, int(time.time()), query))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")


def get_user_queries(user_id):
    with sqlite3.connect(PHOTOS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timestamp, query FROM UserQueries WHERE user_id = ? ORDER BY timestamp DESC", (user_id,)
        )
        rows: Union[List[tuple[int, str]], None] = cursor.fetchall()
        queries: Dict[int, str] = {row[0]: row[1] for row in rows}
        return UserQuery(user_id, queries)


def get_last_queries(amount: int) -> List['UserQuery']:
    with sqlite3.connect(PHOTOS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, timestamp, query FROM UserQueries ORDER BY timestamp DESC LIMIT ?", (amount,)
        )
        rows = cursor.fetchall()
        query_objects = []
        for user_id, timestamp, query in rows:
            query_objects.append(UserQuery(user_id, {timestamp: query}))
        return query_objects


if __name__ == '__main__':
    print(time.time())
