from aiogram import Router, F
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from keyboards.main_menu import main_menu
from config.db_settings import main_database
from models.db_utils import get_database_connection, close_database_connection
from models.db_queries import get_user_profile, get_user_profile_full
from utils.calculations import calculate_age
from utils.logging import setup_logger

router = Router()

logger = setup_logger()

@router.message(F.text == "/start")
async def cmd_start(message: Message, state: FSMContext):
    logger.info(f"Получена команда /start от пользователя {message.from_user.id} ({message.from_user.username})")
    
    user_id = message.from_user.id
    username = message.from_user.username

    try:
        logger.info(f"Подключение к базе данных для пользователя {user_id}")
        conn, cursor = get_database_connection(main_database)

        logger.info(f"Попытка получить профиль пользователя {user_id} из базы данных")
        profile = get_user_profile_full(user_id, cursor)

        logger.info(f"Закрытие соединения с базой данных для пользователя {user_id}")
        close_database_connection(conn)
    except Exception as e:
        logger.error(f"Ошибка при работе с базой данных для пользователя {user_id}: {e}")
        await message.answer("Произошла ошибка при доступе к базе данных. Пожалуйста, попробуйте позже.")
        return

    if profile:
        name, birth_date, city, height, weight, gender, prefered_water, prefered_calories, prefered_workout, created_at = profile
        age = calculate_age(birth_date)
        gender_display = "Мужской" if gender.lower() == "м" else "Женский"
        
        logger.info(f"Профиль для пользователя {user_id} найден: {profile}")
        await message.answer(
            f"Ваш профиль:\n"
            f"Имя: {name}\n"
            f"Дата рождения: {birth_date}\n"
            f"Возраст: {age} лет\nГород: {city}\n"
            f"Рост: {height} см\nВес: {weight} кг\nПол: {gender_display}\n"
            f"Ежедневная норма воды: {prefered_water} мл\n"
            f"Ежедневная норма калорий: {prefered_calories} ккал\n"
            f"Предпочитаемое время активности: {prefered_workout} минут",
            reply_markup=main_menu
        )
    else:
        logger.warning(f"Профиль для пользователя {user_id} не найден.")
        await message.answer(
            "Привет! Используйте /set_profile, чтобы настроить свой профиль.",
            reply_markup=main_menu
        )
