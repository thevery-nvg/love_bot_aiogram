from enum import Enum
from aiogram.filters.callback_data import CallbackData
from src.keyboards.base import InlineConstructor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LoginUrl, CallbackGame
import hashlib
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton



def get_md5_hash(s: str) -> str:
    return hashlib.md5(s.encode('utf-8')).hexdigest()


class Questions(str, Enum):
    register ='register'
    start='start'
    gender_male = 'gender_male'
    gender_female = 'gender_female'
    looking_for_male = 'looking_for_male'
    looking_for_female = 'looking_for_female'
    looking_for_doesntmatter = 'looking_for_doesntmatter'
    more_photo = 'more_photo'
    done_filling = 'done_filling'


class Anketa:
    #TODO: create states
    pass

class QuestionAction(CallbackData, prefix='#q_action'):
    question: Questions


ask_gender_actions = [
    {'text': 'Male', 'cb': QuestionAction(question=Questions.looking_for_male)},
    {'text': 'Female', 'cb': QuestionAction(question=Questions.looking_for_female)},
]

ask_who_find_actions = [
    {'text': 'Male', 'cd': QuestionAction(question=Questions.looking_for_male)},
    {'text': 'Female', 'cd': QuestionAction(question=Questions.looking_for_female)},
    {'text': "Doesn\'t matter", "cb": QuestionAction(question=Questions.looking_for_doesntmatter)},
]

more_photo_actions = [
    {'text': 'One more photo', 'cd': QuestionAction(question=Questions.more_photo)}
]

register_actions = [
    {'text': 'get registered', 'cd': QuestionAction(question=Questions.register)}
]

start_actions = [
    {'text': 'START', 'cd': QuestionAction(question=Questions.start)}
]
done_filling_actions = [
    {'text': 'Done', 'cd': QuestionAction(question=Questions.done_filling)}
]
register_keyboard = InlineConstructor.create_kb(register_actions, [1])
start_filling_keyboard = InlineConstructor.create_kb(start_actions, [1])
gender_keyboard = InlineConstructor.create_kb(ask_gender_actions, [2])
looking_for_keyboard = InlineConstructor.create_kb(ask_who_find_actions, [3])
more_photo_keyboard = InlineConstructor.create_kb(more_photo_actions, [1])
get_location_keyboard = ReplyKeyboardMarkup(
    resize_keyboard=True,
    keyboard=[[KeyboardButton(text='Send location', request_location=True)]],
    one_time_keyboard=True)
done_filling_keyboard = InlineConstructor.create_kb(done_filling_actions, [1])
