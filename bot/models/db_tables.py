import sqlite3
from utils.logging import setup_logger

logger = setup_logger()

def setup_users(conn, cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            birth_date DATE NOT NULL,
            weight REAL NOT NULL,
            height REAL NOT NULL,
            gender TEXT NOT NULL,
            city TEXT NOT NULL,
            prefered_water INTEGER DEFAULT 0,
            prefered_calories INTEGER DEFAULT 0,
            prefered_workout INTEGER DEFAULT 0,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    logger.debug("Создана (IF NOT EXISTS) таблица users.")


def setup_user_goals(conn, cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS user_goals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            calories_goal INTEGER NOT NULL,
            water_goal REAL NOT NULL,
            workout_goal INTEGER NOT NULL,
            updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    logger.debug("Создана (IF NOT EXISTS) таблица user_goals.")

def setup_workouts(conn, cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS workouts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            workout_type TEXT NOT NULL,
            duration INTEGER, -- Продолжительность в минутах
            calories_burned REAL, -- Сожжённые калории
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    logger.debug("Создана (IF NOT EXISTS) таблица workouts.")

def setup_calorie_intake(conn, cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS calorie_intake (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            calories REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    logger.debug("Создана (IF NOT EXISTS) таблица calorie_intake.")

def setup_water_intake(conn, cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS water_intake (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            date DATE NOT NULL,
            water_consumed REAL NOT NULL,
            FOREIGN KEY (user_id) REFERENCES users(id)
        );
    """)
    conn.commit()
    logger.debug("Создана (IF NOT EXISTS) таблица water_intake.")

def setup_weather(conn, cursor):
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS weather (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            city TEXT NOT NULL,
            date DATE NOT NULL,
            temperature REAL NOT NULL
        );
    """)
    conn.commit()
    logger.debug("Создана (IF NOT EXISTS) таблица weather.")