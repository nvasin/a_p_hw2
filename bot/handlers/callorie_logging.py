from aiogram import Router, F
from aiogram.types import Message

from config.db_settings import main_database
from models.db_utils import get_database_connection, close_database_connection
from models.db_queries import log_calories, get_calories_total_today, last_logged_user_norms
from utils.openfoodfacts_api import get_food_info
from utils.logging import setup_logger

logger = setup_logger()

router = Router()

@router.message(F.text.startswith("/log_calories"))
async def handle_log_calories(message: Message):
    logger.info(f"Получена команда /log_calories")
    try:
        user_id = message.from_user.id
        args = message.text.split(maxsplit=1)
        if len(args) != 2:
            await message.reply(
                "Пожалуйста, введите количество калорий или название продукта после команды. "
                "Например:\n- /log_calories 500\n- /log_calories яблоко"
            )
            return

        input_value = args[1]

        # Проверяем, ввел ли пользователь число
        try:
            amount = int(input_value)
            if amount <= 0:
                await message.reply("Количество калорий должно быть положительным числом.")
                return
        except ValueError:
            # Если это не число, пробуем найти информацию о продукте
            food_info = get_food_info(input_value)
            if not food_info:
                await message.reply("Не удалось найти информацию о продукте. Уточните название и попробуйте снова.")
                return

            product_name = food_info['name']
            amount = food_info['calories']

            if amount == 0:
                await message.reply(f"К сожалению, калорийность продукта '{product_name}' не найдена.")
                return

            await message.reply(f"Продукт: {product_name} добавлен ({amount} ккал на 100 г).")

        # Подключение к базе данных
        conn, cursor = get_database_connection(main_database)

        # Получаем последнюю запись норм пользователя
        last_norms = last_logged_user_norms(user_id, conn, cursor)
        if not last_norms:
            await message.reply("Не удалось определить вашу дневную норму калорий. Убедитесь, что ваш профиль настроен.")
            close_database_connection(conn)
            return

        # Извлекаем дневную норму калорий из последней записи
        daily_calories_goal, _, _, _ = last_norms

        # Логируем калории в базу данных
        log_calories(cursor, user_id, amount)
        conn.commit()

        # Получаем суммарное количество потребленных калорий за день
        total_today = get_calories_total_today(user_id, cursor)

        # Закрываем соединение с базой данных
        close_database_connection(conn)

        # Расчет оставшегося количества калорий
        remaining = max(0, daily_calories_goal - total_today)

        await message.reply(
            f"Вы потребили {amount} ккал. Всего за сегодня: {total_today} ккал. До нормы осталось: {remaining} ккал."
        )
    except Exception as e:
        await message.reply("Произошла ошибка при обработке данных.")
        print(e)
