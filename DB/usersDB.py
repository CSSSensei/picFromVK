import sqlite3
import os
import time
from dataclasses import dataclass
from typing import Union, List, Dict, Optional

USERS_DB = f'{os.path.dirname(__file__)}/usersDB.db'
conn_loc = sqlite3.connect(USERS_DB)
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
    CREATE TABLE IF NOT EXISTS Songs (
        unique_tg_id TEXT PRIMARY KEY,
        url TEXT,
        title TEXT,
        artist TEXT,
        yandex_song_id TEXT,
        album_id TEXT
    )
''')

cursor_loc.execute('''
    CREATE TABLE IF NOT EXISTS UserQueries (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        query TEXT,
        FOREIGN KEY (user_id) REFERENCES users_info(user_id)
    )
''')

cursor_loc.execute('''
    CREATE TABLE IF NOT EXISTS SongRequests (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        unique_tg_id INTEGER,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        FOREIGN KEY (user_id) REFERENCES users_info(user_id),
        FOREIGN KEY (unique_tg_id) REFERENCES Songs(unique_tg_id)
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


@dataclass
class Song:
    unique_id: Optional[str]
    url: Optional[str]
    title: str
    artists: str
    yandex_song_id: str
    album_id: str
    path: Optional[str] = None


@dataclass
class MusicQuery:
    user_id: int
    time: int
    song: Song


def add_user(user_id: int, username: Optional[str] = None) -> None:
    try:
        with sqlite3.connect(USERS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO users_info (user_id, username) 
                VALUES (?, ?)
                ON CONFLICT(user_id) DO UPDATE SET 
                username = CASE
                    WHEN excluded.username IS NOT NULL THEN excluded.username
                    ELSE users_info.username  -- оставляем текущее значение
                END
            ''', (user_id, username))
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")


def get_users_from_db() -> List['UserSets']:
    with sqlite3.connect(USERS_DB) as conn:
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
        with sqlite3.connect(USERS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users_info SET admin=? WHERE user_id=?",
                           (True, user_id))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")


def set_public_name(user_id: int, show_name: bool = True):
    try:
        add_user(user_id)
        with sqlite3.connect(USERS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("UPDATE users_info SET public_preview=? WHERE user_id=?",
                           (show_name, user_id))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")


def get_user(user_id: Optional[int] = None, username: Optional[str] = None) -> Optional['UserSets']:
    with sqlite3.connect(USERS_DB) as conn:
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
        with sqlite3.connect(USERS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO UserQueries (user_id, timestamp, query) VALUES (?, ?, ?)",
                           (user_id, int(time.time()), query))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")


def get_user_queries(user_id):
    with sqlite3.connect(USERS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT timestamp, query FROM UserQueries WHERE user_id = ? ORDER BY timestamp DESC", (user_id,)
        )
        rows: Union[List[tuple[int, str]], None] = cursor.fetchall()
        queries: Dict[int, str] = {row[0]: row[1] for row in rows}
        return UserQuery(user_id, queries)


def get_last_queries(amount: int) -> List['UserQuery']:
    with sqlite3.connect(USERS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user_id, timestamp, query FROM UserQueries ORDER BY timestamp DESC LIMIT ?", (amount,)
        )
        rows = cursor.fetchall()
        query_objects = []
        for user_id, timestamp, query in rows:
            query_objects.append(UserQuery(user_id, {timestamp: query}))
        return query_objects


def get_song_info(yandex_song_id, album_id):
    with sqlite3.connect(USERS_DB) as conn:
        cursor = conn.cursor()

        cursor.execute('''
            SELECT * FROM Songs WHERE yandex_song_id = ? AND album_id = ?''', (yandex_song_id, album_id))

        song_info = cursor.fetchone()
        return Song(*song_info) if song_info else None


def add_song(song: Song):
    with sqlite3.connect(USERS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO Songs (unique_tg_id, url, title, artist, yandex_song_id, album_id)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (song.unique_id, song.url, song.title, song.artists, song.yandex_song_id, song.album_id))

        conn.commit()


def add_music_query(user_id: int, username: str, song_unique_id: str):
    try:
        add_user(user_id, username)
        with sqlite3.connect(USERS_DB) as conn:
            cursor = conn.cursor()
            cursor.execute("INSERT INTO SongRequests (user_id, unique_tg_id, timestamp) VALUES (?, ?, ?)",
                           (user_id, song_unique_id, int(time.time())))
            conn.commit()
    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")


def get_len_music_queries(user_id: int) -> int:
    with sqlite3.connect(USERS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT unique_tg_id, timestamp FROM SongRequests WHERE user_id = ?''', (user_id,))

        rows = cursor.fetchall()
        return len(rows)


def get_music_queries_by_user(user_id: int) -> List[MusicQuery]:
    with sqlite3.connect(USERS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT unique_tg_id, timestamp FROM SongRequests WHERE user_id = ? ORDER BY timestamp DESC''', (user_id,))

        rows = cursor.fetchall()
        music_queries = []

        for unique_tg_id, timestamp in rows:
            song = get_song_by_unique_tg_id(unique_tg_id)
            if song:
                music_queries.append(MusicQuery(user_id=user_id, time=timestamp, song=song))
        return music_queries


def get_song_by_unique_tg_id(unique_tg_id: str) -> Optional[Song]:
    with sqlite3.connect(USERS_DB) as conn:
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM Songs WHERE unique_tg_id = ?''', (unique_tg_id,))

        row = cursor.fetchone()

        if row:
            return Song(
                unique_id=row[0],  # unique_tg_id, обычно он будет первым
                url=row[1],  # url
                title=row[2],  # title
                artists=row[3],  # artist
                yandex_song_id=row[4],  # yandex_song_id
                album_id=row[5]  # album_id
            )
        return None


if __name__ == '__main__':
    print(time.time())
