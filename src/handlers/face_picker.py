from aiogram import types, Bot, Router, F
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto, Location

from src.database.db import freeze_user, unfreeze_user, \
    get_nearby_and_same_city_users, calculate_distance, update_user
from src.database.models import User
from src.keyboards.questionary import get_location_keyboard
from src.keyboards.user_profile import *
from src.states.fsm import Anketa
from src.utils.validators import validate_city
from src.handlers.register import ask_age

face_picker_router = Router()


@face_picker_router.callback_query(ProfileOptions.face_picker)
async def face_picker(call: types.CallbackQuery, state: FSMContext, dbpool):
    data = await state.get_data()
    me = data.get('me')
    if 'people' not in data or not data['people']:
        data['people'] = iter(await get_nearby_and_same_city_users(
            dbpool, me.location, 10, me.city, me.looking_for
        ))
    try:
        booty = next(data['people'])
    except StopIteration:
        data['people'] = iter(await get_nearby_and_same_city_users(
            dbpool, me.location, 10, me.city, me.looking_for
        ))
        booty = next(data['people'])
    data = await state.get_data()
    me = data.get('me')
    if 'people' not in data or not data['people']:
        data['people'] = iter(await get_nearby_and_same_city_users(
            dbpool, me.location, 5, me.city, me.looking_for
        ))
    try:
        booty = next(data['people'])
    except StopIteration:
        data['people'] = iter(await get_nearby_and_same_city_users(
            dbpool, me.location, 5, me.city, me.looking_for
        ))
        booty = next(data['people'])
    media = [InputMediaPhoto(media=booty.photos[0])]