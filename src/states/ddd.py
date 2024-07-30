from aiogram.fsm.state import StatesGroup, State


class Anketa(StatesGroup):
    age = State()
    gender = State()
    looking_for = State()
    location = State()
    name = State()
    description = State()
    photo = State()
    done = State()