from aiogram.filters.callback_data import CallbackData

from src.keyboards.base import InlineConstructor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LoginUrl, CallbackGame
import hashlib


def get_md5_hash(s: str) -> str:
    return hashlib.md5(s.encode('utf-8')).hexdigest()


class ExampleCallbackData(CallbackData, prefix="example"):
    action: str
    value: int


# Пример данных для кнопок

actions = [
    {"text": "Button 1", "cb": ExampleCallbackData(action="action", value=1)},
    {"text": "Button 1", "cb": ExampleCallbackData(action="action", value=2)},
    {"text": "Button 1", "cb": ExampleCallbackData(action="action", value=3)},
    {"text": "Button 1", "cb": ExampleCallbackData(action="action", value=4)},
    # {"text": "Button 2", "url": "https://google.com"},
    # {"text": "Button 3", "login_url": LoginUrl(url="https://example.com/login")},
    # {"text": "Button 4", "callback_game": CallbackGame()},
]

# Пример схемы: две строки, первая с двумя кнопками, вторая с двумя кнопками
schema = [2, 2]

# Создаем клавиатуру
keyboard = InlineConstructor.create_kb(actions, schema)
