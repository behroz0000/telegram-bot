from datetime import datetime, timedelta
import sqlite3


def init_db():
    conn = sqlite3.connect("kino_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            vip_until TIMESTAMP DEFAULT NULL
        )
    """)
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS movies (
            code INTEGER PRIMARY KEY,
            title TEXT NOT NULL,
            file_id TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_user(user_id: int):
    conn = sqlite3.connect("kino_bot.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,)
    )
    conn.commit()
    conn.close()


def set_vip(user_id: int, days: int):
    conn = sqlite3.connect("kino_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT vip_until FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()

    now = datetime.now()
    if row and row[0]:
        current_vip = datetime.fromisoformat(row[0])
        start_date = max(now, current_vip)
    else:
        start_date = now

    new_vip = start_date + timedelta(days=days)
    cursor.execute(
        "UPDATE users SET vip_until = ? WHERE user_id = ?",
        (new_vip.isoformat(), user_id),
    )
    conn.commit()
    conn.close()
    return new_vip.strftime("%d.%m.%Y %H:%M")


def is_vip(user_id: int) -> bool:
    conn = sqlite3.connect("kino_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT vip_until FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        return datetime.fromisoformat(row[0]) > datetime.now()
    return False


def get_vip_expiry(user_id: int):
    conn = sqlite3.connect("kino_bot.db")
    cursor = conn.cursor()
    cursor.execute("SELECT vip_until FROM users WHERE user_id = ?", (user_id,))
    row = cursor.fetchone()
    conn.close()
    if row and row[0]:
        dt = datetime.fromisoformat(row[0])
        if dt > datetime.now():
            return dt.strftime("%d.%m.%Y %H:%M")
    return None


def add_movie(code: int, title: str, file_id: str):
    conn = sqlite3.connect("kino_bot.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT OR REPLACE INTO movies (code, title, file_id) VALUES (?, ?, ?)",
        (code, title, file_id),
    )
    conn.commit()
    conn.close()


def get_movie_by_code(code: int):
    conn = sqlite3.connect("kino_bot.db")
    cursor = conn.cursor()
    cursor.execute(
        "SELECT title, file_id FROM movies WHERE code = ?", (code,)
    )
    row = cursor.fetchone()
    conn.close()
    return row