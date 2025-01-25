import sqlite3
from utils.logging import setup_logger

logger = setup_logger()


def get_database_connection(db_name):
    conn = sqlite3.connect(db_name)
    cursor = conn.cursor()
    logger.debug(f"Для БД {db_name} открыто соединение conn: {conn}, cursor: {cursor}")
    return conn, cursor


def close_database_connection(conn):
    if conn:
        conn.close()
        logger.debug(f"Закрыто соединение conn: {conn}")