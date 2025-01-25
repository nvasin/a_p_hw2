from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="/check_progress"),KeyboardButton(text="/stats")],
        [KeyboardButton(text="/log_water"),KeyboardButton(text="/log_calories"),KeyboardButton(text="/log_workout")],
        [KeyboardButton(text="/set_profile")]
    ],
    resize_keyboard=True
)