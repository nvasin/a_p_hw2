import requests
from datetime import datetime
from utils.logging import setup_logger
from models.db_queries import (
    is_weather_logged_today,
    log_weather,
    get_weather_for_today,
    get_user_city
)
from config.api import WEATHER_API_URL, WEATHER_API_KEY

logger = setup_logger()

API_URL = WEATHER_API_URL
API_KEY = WEATHER_API_KEY



def fetch_weather_from_api(city):
    """
    Получает текущую информацию о погоде из API weatherstack.

    :param city: Название города
    :return: Температура в городе (float) или None, если запрос не удался
    """
    params = {
        "access_key": API_KEY,
        "query": city
    }

    try:
        response = requests.get(API_URL, params=params)
        response.raise_for_status()  # Проверка успешного запроса
        data = response.json()

        if "current" in data:
            temperature = data["current"]["temperature"]
            logger.debug(f"Получена температура {temperature}°C для города {city}.")
            return temperature
        else:
            logger.error(f"Ошибка API: {data}")
            return None
    except Exception as e:
        logger.error(f"Ошибка при запросе погоды для города {city}: {e}")
        return None


def get_or_fetch_weather(user_id, conn, cursor):
    """
    Получает текущую температуру для пользователя: либо из базы, либо из API.

    :param user_id: ID пользователя
    :param conn: Подключение к базе данных
    :param cursor: Курсор базы данных
    :return: Температура (float) или None, если данные недоступны
    """
    # Получаем город пользователя
    city = get_user_city(user_id, cursor)
    if not city:
        logger.error(f"Город для пользователя {user_id} не найден.")
        return None

    # Проверяем, есть ли запись о погоде на сегодня
    if is_weather_logged_today(city, cursor):
        logger.debug(f"Информация о погоде для {city} уже записана.")
        return get_weather_for_today(city, cursor)

    # Если записи нет, запрашиваем погоду из API
    temperature = fetch_weather_from_api(city)
    if temperature is not None:
        log_weather(city, temperature, conn, cursor)

    return temperature
