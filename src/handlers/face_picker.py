from aiogram import types, Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto
from src.keyboards.face_picker_kbd import face_picker_kbd, FacePickerAction, FacePickerOptions

from src.database.db import get_nearby_and_same_city_users

from src.keyboards.user_profile import *

from src.utils.misc import PairIterator

face_picker_router = Router()


@face_picker_router.callback_query(ProfileAction.filter(F.action == ProfileOptions.face_picker),
                                   FacePickerAction.filter(F.action == FacePickerOptions.left),
                                   FacePickerAction.filter(F.action == FacePickerOptions.right))
async def face_picker(call: types.CallbackQuery, state: FSMContext, dbpool, bot: Bot):
    data = await state.get_data()
    me = data.get('me')
    if 'photos' not in data or not data['photos']:
        data['photos'] = PairIterator(await get_nearby_and_same_city_users(
            dbpool, me.location, 10, me.city, me.looking_for
        ))
    try:
        photos = next(data['photos'])
    except StopIteration:
        data['people'] = PairIterator(await get_nearby_and_same_city_users(
            dbpool, me.location, 10, me.city, me.looking_for
        ))
        photos = next(data['photos'])
        await state.update_data(photos=data['photos'])
    media = [InputMediaPhoto(media=photo) for photo in photos]
    await bot.send_media_group(chat_id=call.message.chat.id, media=media)
    await bot.send_message(chat_id=call.message.chat.id,
                           text=f'Выберите фото',
                           reply_markup=face_picker_kbd)
