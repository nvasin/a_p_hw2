from aiogram import Router, types, F
from aiogram.types import Message

from config.db_settings import main_database
from models.db_utils import get_database_connection, close_database_connection
from models.db_queries import log_water, get_water_total_today, last_logged_user_norms



router = Router()

@router.message(F.text.startswith("/log_water"))
async def handle_log_water(message: Message):
    try:
        user_id = message.from_user.id
        args = message.text.split()
        if len(args) != 2:
            await message.reply("Пожалуйста, введите количество воды после команды. Например: /log_water 250")
            return

        amount = int(args[1])
        if amount <= 0:
            await message.reply("Количество воды должно быть положительным числом.")
            return

        # Подключение к базе данных
        conn, cursor = get_database_connection(main_database)

        # Получаем последнюю запись норм пользователя
        last_norms = last_logged_user_norms(user_id, conn, cursor)
        if not last_norms:
            await message.reply("Не удалось определить вашу дневную норму воды. Убедитесь, что ваш профиль настроен.")
            close_database_connection(conn)
            return

        # Извлекаем дневную норму воды из последней записи
        _, daily_water_goal, _, _ = last_norms

        # Логируем воду в базу данных
        log_water(cursor, user_id, amount)
        conn.commit()

        # Получаем суммарное количество выпитой воды за день
        total_today = get_water_total_today(user_id, cursor)

        # Закрываем соединение с базой данных
        close_database_connection(conn)

        # Расчет оставшегося количества
        remaining = max(0, daily_water_goal - total_today)

        await message.reply(
            f"Вы выпили {amount} мл воды. Всего за сегодня: {total_today} мл. До нормы осталось: {remaining} мл."
        )
    except ValueError:
        await message.reply("Пожалуйста, введите корректное количество воды в миллилитрах.")
    except Exception as e:
        await message.reply("Произошла ошибка при логировании воды.")
        print(e)

