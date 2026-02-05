from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="📦 Orders")],
        [KeyboardButton(text="💳 Your UPI Account")]
    ],
    resize_keyboard=True
)
