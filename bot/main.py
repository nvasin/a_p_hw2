import os
from aiogram import Bot, Dispatcher, F, types
from aiogram.types import Message, ReplyKeyboardMarkup, KeyboardButton, InputFile, FSInputFile
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.filters import Command 
import asyncio
#from aiogram.utils import executor

from io import BytesIO

from config.bot_token import BOT_TOKEN
from config.db_settings import main_database
from models.db_utils import get_database_connection, close_database_connection
from models.db_tables import setup_users, setup_user_goals, setup_workouts, setup_calorie_intake, setup_water_intake, setup_weather
from utils.user_stats import generate_user_stats

from handlers import  start, profile, progress, water_logging, callorie_logging, workout_logging

from utils.logging import setup_logger

logger = setup_logger()


API_TOKEN = BOT_TOKEN


bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(storage=storage)

# Настройка базы данных
logger.debug(f"Подготовка БД и таблиц начата")
conn, cursor = get_database_connection(main_database)

setup_users(conn, cursor)
setup_user_goals(conn, cursor)
setup_workouts(conn, cursor)
setup_calorie_intake(conn, cursor)
setup_water_intake(conn, cursor)
setup_weather(conn, cursor)

close_database_connection(conn)
logger.debug(f"Подготовка БД и таблиц закончена")


dp.include_router(start.router)
dp.include_router(profile.router)
dp.include_router(progress.router)
dp.include_router(water_logging.router)
dp.include_router(callorie_logging.router)
dp.include_router(workout_logging.router)

from aiogram.types import BufferedInputFile

@dp.message(Command(commands=["stats"]))
async def send_stats(message: Message):
    logger.debug(f"Получена команда /stats")
    user_id = message.from_user.id 
    stats_image, caption = generate_user_stats(user_id)
    stats_image.seek(0)
    image_file = BufferedInputFile(file=stats_image.read(), filename="user_stats.png")
    await message.answer_photo(photo=image_file, caption=caption)


async def main():
    try:
        await dp.start_polling(bot)
    finally:
        await bot.session.close()
        conn.close()

if __name__ == "__main__":
    asyncio.run(main())
