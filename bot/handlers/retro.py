from aiogram import Bot, Dispatcher, types
from aiogram.types import InputFile

from config.bot_token import BOT_TOKEN

from io import BytesIO

bot = Bot(token=BOT_TOKEN)

dp = Dispatcher(bot)

@dp.message_handler(commands=['stats'])
async def send_stats(message: types.Message):
    user_id = message.from_user.id  # Получаем ID пользователя Telegram
    # Генерируем статистику
    stats_image, caption = generate_user_stats(user_id)
    
    # Отправляем изображение с подписью
    image_file = InputFile(stats_image, filename="user_stats.png")
    await bot.send_photo(chat_id=message.chat.id, photo=image_file, caption=caption)