from enum import Enum
from aiogram.filters.callback_data import CallbackData
from src.keyboards.base import InlineConstructor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LoginUrl, CallbackGame
import hashlib
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


def get_md5_hash(s: str) -> str:
    return hashlib.md5(s.encode('utf-8')).hexdigest()


class Questions(str, Enum):
    register = 'register'
    start = 'start'
    gender_male = 'male'
    gender_female = 'female'
    looking_for_male = 'looking_for_male'
    looking_for_female = 'looking_for_female'
    looking_for_anything = 'looking_for_anything'
    more_photo = 'more_photo'
    done_filling = 'done_filling'


class QuestionAction(CallbackData, prefix='#ask_action'):
    question: Questions
    value: int


ask_gender_actions = [
    {'text': 'Парень', 'cb': QuestionAction(question=Questions.gender_male, value=1)},
    {'text': 'Девушка', 'cb': QuestionAction(question=Questions.gender_female, value=1)},
]

ask_looking_for_actions = [
    {'text': 'Парня', 'cb': QuestionAction(question=Questions.looking_for_male, value=1)},
    {'text': 'Девушку', 'cb': QuestionAction(question=Questions.looking_for_female, value=1)},
    {'text': "Любого", "cb": QuestionAction(question=Questions.looking_for_anything,
                                            value=1)},
]

register_actions = [
    {'text': 'Зарегистрироваться',
     'cb': QuestionAction(question=Questions.register, value=1)}
]

start_actions = [
    {'text': 'Начать!', 'cb': QuestionAction(question=Questions.start, value=1)}
]
done_filling_actions = [
    {'text': 'Готово', 'cb': QuestionAction(question=Questions.done_filling, value=1)}
]

get_location_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[[KeyboardButton(text='Отправить геопозицию', request_location=True)]],
    one_time_keyboard=True)

register_keyboard = InlineConstructor.create_kb(register_actions, [1])
start_filling_keyboard = InlineConstructor.create_kb(start_actions, [1])
gender_keyboard = InlineConstructor.create_kb(ask_gender_actions, [2])
looking_for_keyboard = InlineConstructor.create_kb(ask_looking_for_actions, [3])
done_filling_keyboard = InlineConstructor.create_kb(done_filling_actions, [1])
