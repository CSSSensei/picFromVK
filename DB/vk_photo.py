import sqlite3
import os
from dataclasses import dataclass

photos_db = f'{os.path.dirname(__file__)}/photos.db'
conn_loc = sqlite3.connect(photos_db)
cursor_loc = conn_loc.cursor()

cursor_loc.execute('''
    CREATE TABLE IF NOT EXISTS photos (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        group_id INTEGER NOT NULL,
        photo_id INTEGER NOT NULL,
        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        UNIQUE(group_id, photo_id)
    )
''')
cursor_loc.close()
conn_loc.close()


@dataclass
class Photo:
    owner_id: int
    photo_id: int


def check_photo(photo_info: Photo):
    try:
        with sqlite3.connect(photos_db) as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT * FROM photos WHERE group_id = ? AND photo_id = ?',
                           (photo_info.owner_id, photo_info.photo_id))
            if cursor.fetchone() is None:
                cursor.execute('INSERT INTO photos (group_id, photo_id) VALUES (?, ?)',
                               (photo_info.owner_id, photo_info.photo_id))
                conn.commit()
                return False
            return True

    except sqlite3.Error as e:
        print(f"Ошибка при работе с базой данных: {e}")
        return None


if __name__ == '__main__':
    with sqlite3.connect(photos_db) as conn:
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM photos')
        print(*cursor.fetchall(), sep='\n')
