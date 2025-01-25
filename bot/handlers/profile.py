from aiogram import Router, F 
from aiogram.types import Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from datetime import datetime

from config.db_settings import main_database
from models.db_utils import get_database_connection, close_database_connection
from models.db_queries import save_user_profile

from utils.calculations import calculate_age
from utils.logging import setup_logger

logger = setup_logger()

router = Router()

class ProfileSetup(StatesGroup):
    waiting_for_name = State()
    waiting_for_birth_date = State()
    waiting_for_city = State()
    waiting_for_height = State()
    waiting_for_weight = State()
    waiting_for_gender = State()
    waiting_for_prefered_water = State()
    waiting_for_prefered_calories = State()
    waiting_for_prefered_workout = State()

@router.message(F.text == "/set_profile")

async def cmd_set_profile(message: Message, state: FSMContext):
    logger.info(f"Получена команда /set_profile")
    await message.answer("Введите ваше имя:")
    await state.set_state(ProfileSetup.waiting_for_name)

@router.message(ProfileSetup.waiting_for_name)
async def process_name(message: Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)
    await message.answer("Отлично! Теперь введите вашу дату рождения (в формате ДД.ММ.ГГГГ):")
    await state.set_state(ProfileSetup.waiting_for_birth_date)

@router.message(ProfileSetup.waiting_for_birth_date)
async def process_birth_date(message: Message, state: FSMContext):
    try:
        birth_date = datetime.strptime(message.text, "%d.%m.%Y").date()
    except ValueError:
        await message.answer("Неверный формат даты. Попробуйте еще раз (ДД.ММ.ГГГГ):")
        return

    await state.update_data(birth_date=birth_date)
    await message.answer("Введите ваш город проживания (на английском):")
    await state.set_state(ProfileSetup.waiting_for_city)

@router.message(ProfileSetup.waiting_for_city)
async def process_city(message: Message, state: FSMContext):
    city = message.text
    await state.update_data(city=city)
    await message.answer("Введите ваш рост в сантиметрах:")
    await state.set_state(ProfileSetup.waiting_for_height)

@router.message(ProfileSetup.waiting_for_height)
async def process_height(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Рост должен быть числом. Попробуйте еще раз:")
        return

    height = int(message.text)
    await state.update_data(height=height)
    await message.answer("Введите ваш вес в килограммах:")
    await state.set_state(ProfileSetup.waiting_for_weight)

@router.message(ProfileSetup.waiting_for_weight)
async def process_weight(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Вес должен быть числом. Попробуйте еще раз:")
        return

    weight = float(message.text)
    await state.update_data(weight=weight)
    await message.answer("Укажите ваш пол (м/ж):")
    await state.set_state(ProfileSetup.waiting_for_gender)

@router.message(ProfileSetup.waiting_for_gender)
async def process_gender(message: Message, state: FSMContext):
    gender = message.text.lower()
    if gender not in ["м", "ж"]:
        await message.answer("Пожалуйста, укажите 'м' или 'ж':")
        return

    await state.update_data(gender=gender)
    await message.answer("Какую норму воды в миллилитрах вы предпочитаете ежедневно?\nВведите 0, если хотите получить рекомендуемое количество.")
    await state.set_state(ProfileSetup.waiting_for_prefered_water)

@router.message(ProfileSetup.waiting_for_prefered_water)
async def process_prefered_water(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите количество мл воды числом:")
        return

    prefered_water = int(message.text)
    await state.update_data(prefered_water=prefered_water)
    await message.answer("Сколько калорий вы хотите потреблять ежедневно?\nВведите 0, если хотите получить рекомендуемое количество.")
    await state.set_state(ProfileSetup.waiting_for_prefered_calories)

@router.message(ProfileSetup.waiting_for_prefered_calories)
async def process_prefered_calories(message: Message, state: FSMContext):
    if not message.text.isdigit():
        await message.answer("Введите количество калорий числом:")
        return

    prefered_calories = int(message.text)
    await state.update_data(prefered_calories=prefered_calories)
    await message.answer("Сколько минут активности в день вы хотели бы поддерживать?\nВведите 0, если хотите получить рекомендуемое количество.")
    await state.set_state(ProfileSetup.waiting_for_prefered_workout)

@router.message(ProfileSetup.waiting_for_prefered_workout)
async def process_prefered_workout(message: Message, state: FSMContext):
    prefered_workout = message.text
    await state.update_data(prefered_workout=prefered_workout)

    user_id = message.from_user.id
    username = message.from_user.username
    user_data = await state.get_data()

    name = user_data.get("name")
    birth_date = user_data.get("birth_date")
    city = user_data.get("city")
    height = user_data.get("height")
    weight = user_data.get("weight")
    gender = user_data.get("gender")
    prefered_water = user_data.get("prefered_water")
    prefered_calories = user_data.get("prefered_calories")
    prefered_workout = user_data.get("prefered_workout")


    conn, cursor = get_database_connection(main_database)

    save_user_profile(
        user_id, username, name, birth_date,
        city, height, weight, gender,
        prefered_water, prefered_calories, prefered_workout,
        conn, cursor
    )

    close_database_connection(conn)

    await message.answer(
        f"Ваш профиль сохранён:\nИмя: {name}\n"
        f"Дата рождения: {birth_date.strftime('%d.%m.%Y')}\n"
        f"Возраст: {calculate_age(birth_date, date_format='%Y-%m-%d')} лет\n"
        f"Город: {city}\nРост: {height} см\nВес: {weight} кг\n"
        f"Пол: {'Мужской' if gender == 'м' else 'Женский'}\n"
        f"Ежедневная норма воды: {prefered_water} мл\n"
        f"Ежедневная норма калорий: {prefered_calories} ккал\n"
        f"Предпочитаемое время активности: {prefered_workout} минут"
    )
    await state.clear()