from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message
from config.db_settings import main_database
from models.db_utils import get_database_connection, close_database_connection
from models.db_queries import log_workout
from utils.logging import setup_logger

router = Router()
logger = setup_logger()

# MET-значения для фиксированных тренировок
MET_VALUES = {
    "бег": 9.8,
    "йога": 2.5,
    "силовая": 6.0,
    "велосипед": 8.0
}

@router.message(F.text.startswith("/log_workout"))
async def handle_log_workout(message: Message):
    logger.info(f"Получена команда /log_workout")
    try:
        user_id = message.from_user.id
        args = message.text.split()
        if len(args) < 3:
            await message.reply("Пожалуйста, введите тип тренировки и продолжительность (в минутах). Например: /log_workout бег 30")
            return

        workout_type = args[1].lower()
        if workout_type not in MET_VALUES and workout_type != "калории":
            await message.reply("Неверный тип тренировки. Доступные варианты: бег, йога, силовая, велосипед.")
            return

        conn, cursor = get_database_connection(main_database)

        # Если пользователь указал "калории", просто сохраняем
        if workout_type == "калории":
            calories_burned = int(args[2])
            log_workout(cursor, user_id, None, None, calories_burned)
            conn.commit()
            await message.reply(f"🏋️‍♂️ Тренировка успешно записана! Сожжено калорий: {calories_burned} ккал.")
            close_database_connection(conn)
            return

        # Если указан тип тренировки, рассчитываем калории
        duration = int(args[2])
        if duration <= 0:
            await message.reply("Продолжительность тренировки должна быть положительным числом.")
            return

        cursor.execute("SELECT weight FROM users WHERE id = ?", (user_id,))
        user_data = cursor.fetchone()
        if not user_data:
            await message.reply("Не удалось найти ваш профиль. Настройте его с помощью команды /set_profile.")
            close_database_connection(conn)
            return

        weight = user_data[0]
        met = MET_VALUES[workout_type]
        calories_burned = weight * met * (duration / 60)  # Рассчёт калорий

        log_workout(cursor, user_id, workout_type, duration, calories_burned)
        conn.commit()

        # Рассчёт дополнительной воды
        additional_water = duration * 10

        await message.reply(
            f"🏋️‍♂️ Тренировка успешно записана!\n"
            f"Тип: {workout_type.capitalize()}\n"
            f"Длительность: {duration} минут\n"
            f"Сожжено калорий: {calories_burned:.1f} ккал\n\n"
            f"💧 Рекомендуется выпить {additional_water} мл воды после тренировки."
        )
        close_database_connection(conn)
    except ValueError:
        await message.reply("Пожалуйста, введите корректное число для длительности или калорий.")
    except Exception as e:
        logger.error(f"Ошибка при логировании тренировки: {e}")
        await message.reply("Произошла ошибка при логировании тренировки.")
