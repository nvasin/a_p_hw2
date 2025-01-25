from datetime import datetime

from aiogram import Router, F
from aiogram.types import Message

from config.db_settings import main_database
from models.db_utils import get_database_connection, close_database_connection
from models.db_queries import (
    get_user_profile_full,
    log_user_norms,
    check_logged_user_norms,
    last_logged_user_norms,
    get_water_total_today,
    get_calories_total_today,
    get_workout_stats_today
)
from utils.calculations import calculate_user_norms, calculate_age
from utils.logging import setup_logger
from utils.weather_api import get_or_fetch_weather

# Температурный порог и дополнительная норма воды
TEMPERATURE_THRESHOLD = 25
ADDITIONAL_WATER = 500

logger = setup_logger()

router = Router()

@router.message(F.text == "/check_progress")
async def cmd_check_progress(message: Message):
    logger.info(f"Получена команда /check_progress от пользователя {message.from_user.id}")
    user_id = message.from_user.id

    conn, cursor = get_database_connection(main_database)

    profile = get_user_profile_full(user_id, cursor)

    if not profile:
        await message.answer("Профиль не найден. Настройте его с помощью команды /set_profile.")
        close_database_connection(conn)
        return

    name, birth_date, city, height, weight, gender, prefered_water, prefered_calories, prefered_workout, created_at = profile
    age = calculate_age(birth_date)

    if prefered_calories > 0:
        calories_goal = prefered_calories
        logger.info(f"Для {user_id} используется пользовательская цель калорий: {calories_goal}")
    else:
        calories_goal = calculate_user_norms(height, weight, age)["calories_goal"]
        logger.info(f"Для {user_id} рассчитана цель калорий: {calories_goal}")

    if prefered_water > 0:
        water_goal = prefered_water
        logger.info(f"Для {user_id} используется пользовательская цель воды: {water_goal}")
    else:

        water_goal = calculate_user_norms(height, weight, age)["water_goal"]
        logger.info(f"Для {user_id} рассчитана цель воды: {water_goal}")

    if prefered_workout > 0:
        workout_goal = prefered_workout
        logger.info(f"Для {user_id} используется пользовательская цель активности: {workout_goal} минут")
    else:
        workout_goal = calculate_user_norms(height, weight, age)["daily_activity_minutes"]
        logger.info(f"Для {user_id} рассчитана цель активности: {workout_goal} минут")

    if check_logged_user_norms(user_id, conn, cursor):

        last_entry = last_logged_user_norms(user_id, conn, cursor)
        if last_entry:
            calories_goal, water_goal, workout_goal, updated_at = last_entry
            logger.info(f"Используем существующую запись норм для {user_id} за {updated_at}.")
    else:

        log_user_norms(user_id, calories_goal, water_goal, workout_goal, conn, cursor)
        logger.info(f"Запись норм для {user_id} добавлена за {datetime.now().date()}.")

    temperature = get_or_fetch_weather(user_id, conn, cursor)
    if temperature is not None and temperature > TEMPERATURE_THRESHOLD:
        logger.info(f"Температура {temperature}°C превышает порог {TEMPERATURE_THRESHOLD}°C. Добавляем {ADDITIONAL_WATER} мл к норме воды.")
        water_goal += ADDITIONAL_WATER

    water_consumed = get_water_total_today(user_id, cursor)
    calories_consumed = get_calories_total_today(user_id, cursor)

    total_workout_duration, total_burnt_calories = get_workout_stats_today(user_id, cursor)
    

    close_database_connection(conn)

    additional_water = ADDITIONAL_WATER if temperature > TEMPERATURE_THRESHOLD else 0
    await message.answer(
        f"📊 Статус на {datetime.now().strftime('%d.%m.%Y')}\n\n"
        f"🌊 Температура {temperature}, в норму воды добавлено {additional_water} мл\n\n"
        f"💧 Вода (мл):\n"
        f"  Норма на день: {water_goal}\n"
        f"  Выпито воды: {water_consumed}\n"
        f"  Осталось выпить: {max(0, water_goal - water_consumed)}\n\n"
        f"🔥 Калории (ккал):\n"
        f"  Норма на день: {calories_goal}\n"
        f"  Калорий потреблено: {calories_consumed}\n"
        f"  Осталось накушоть: {max(0, calories_goal - calories_consumed)}\n\n"
        f"🏃‍♂️ Активность (минуты):\n"
        f"  Цель: {workout_goal}\n"
        f"  Текущая активность: {total_workout_duration}\n"
        f"  Сожжено калорий: {total_burnt_calories}\n"
        f"  Осталось: {max(0,workout_goal- total_workout_duration)}"

    )
