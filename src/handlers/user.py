from aiogram import types, Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import InputMediaPhoto

from src.database.db import freeze_user, unfreeze_user, \
    get_nearby_and_same_city_users, calculate_distance, update_user
from src.database.models import User
from src.keyboards.questionary import get_location_keyboard
from src.keyboards.user_profile import *
from src.states.fsm import Anketa
from src.utils.validators import validate_city
from src.handlers.register import ask_age

registered_user_router = Router()


@registered_user_router.callback_query(ProfileAction.filter(F.action == ProfileOptions.view_people))
async def view_people(call: types.CallbackQuery, state: FSMContext, bot: Bot, dbpool):
    data = await state.get_data()
    me = data.get('me')
    if not data.get('people'):
        people = await get_nearby_and_same_city_users(dbpool,
                                                      me.location,
                                                      5,
                                                      me.city,
                                                      me.gender)
        data['people'] = iter(people)
    try:
        booty = data['people'].__next__()
    except StopIteration:
        ...
    else:
        media = [InputMediaPhoto(media=photo) for photo in booty.photos]
        msg = (f"name {booty.name}\n"
               f"{calculate_distance(dbpool, me, booty)}m from you"
               f"age: {booty.age}\n"
               f"gender: {booty.gender}\n"
               f"looking for: {booty.looking_for}\n"
               f"description: {booty.description}\n")
        await bot.send_media_group(chat_id=call.from_user.id, media=media)
        await bot.send_message(call.from_user.id, msg, reply_markup=viewing_keyboard)
        await state.update_data(people=data['people'])
        await state.update_data(booty=booty)


@registered_user_router.callback_query(
    ProfileAction.filter(F.action == ProfileOptions.like))
async def like(call: types.CallbackQuery, state: FSMContext, bot: Bot, dbpool):
    data = await state.get_data()
    booty: User = data.get('booty')
    me: User = data.get('me')
    if me in booty.liker:
        me.matched_with.append(booty)
        booty.matched_with.append(me)
        booty.liker.remove(me)
        await update_user(dbpool, me)
        await update_user(dbpool, booty)
        await bot.send_message(me.id, f"Есть взаимная сипатия !https://t.me/{booty.username}",
                               reply_markup=continue_keyboard)
        await bot.send_message(booty.id, f"Есть взаимная сипатия! https://t.me/{me.username}")
    else:
        me.liker.append(booty)
        booty.liked_by.append(me)
        await update_user(dbpool, me)
        await update_user(dbpool, booty)
        await state.update_data(booty=None, me=me)


@registered_user_router.callback_query(
    ProfileAction.filter(F.action == ProfileOptions.dislike))
async def dislike(call: types.CallbackQuery, state: FSMContext, bot: Bot, dbpool):
    data = await state.get_data()
    booty: User = data.get('booty')
    me: User = data.get('me')
    booty.liker.remove(me.id)
    await update_user(dbpool, booty)
    await view_people(call, state, bot, dbpool)


@registered_user_router.callback_query(
    ProfileAction.filter(F.action == ProfileOptions.unfreeze_profile))
async def view_my_profile(call: types.CallbackQuery, state: FSMContext, bot: Bot, dbpool):
    data = await state.get_data()
    me = data.get('me')
    msg = (f"name {me.name}\n"
           f"age: {me.age}\n"
           f"gender: {me.gender}\n"
           f"looking for: {me.looking_for}\n"
           f"description: {me.description}\n")
    media = [InputMediaPhoto(media=photo) for photo in me.photos]
    await bot.send_media_group(chat_id=call.from_user.id, media=media)
    await bot.send_message(call.from_user.id, msg, reply_markup=user_profile_keyboard)


@registered_user_router.callback_query(
    ProfileAction.filter(F.action == ProfileOptions.update_location))
async def refresh_location(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await bot.send_message(call.from_user.id,
                           "Отправьте ваше местоположение или напишите город",
                           reply_markup=get_location_keyboard)
    await state.set_state(Anketa.location)


@registered_user_router.message(Anketa.location)
async def receive_location(message: types.Message,
                           bot: Bot,
                           dbpool,
                           state: FSMContext) -> None:
    data = await state.get_data()
    if message.location is not None:
        location = message.location
        me = await update_user(session=dbpool,
                               user=data.get('me'),
                               location=location)
        await state.update_data(me=me)
        await state.clear()
    else:
        city = message.text.strip()
        if validate_city(city):
            await update_user(session=dbpool,
                              user=data.get('me'),
                              city=city)
            await state.set_state(state=None)
        else:
            await bot.send_message(message.from_user.id, "Введите корректный город")


@registered_user_router.callback_query(
    ProfileAction.filter(F.action == ProfileOptions.refill_profile))
async def refill_profile(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await state.set_state(Anketa.age)
    await ask_age(call, bot)


@registered_user_router.callback_query(
    ProfileAction.filter(F.action == ProfileOptions.freeze_profile))
async def freeze_profile(call: types.CallbackQuery, state: FSMContext, bot: Bot, dbpool):
    data = await state.get_data()
    me = data.get('me')
    me = await freeze_user(dbpool, me)
    await state.update_data(me=me)
    await bot.send_message(call.from_user.id, "Профиль успешно заморожен")


@registered_user_router.callback_query(
    ProfileAction.filter(F.action == ProfileOptions.unfreeze_profile))
async def unfreeze_profile(call: types.CallbackQuery, state: FSMContext, bot: Bot, dbpool):
    data = await state.get_data()
    me = data.get('me')
    me = await unfreeze_user(dbpool, me)
    await state.update_data(me=me)
    await bot.send_message(call.from_user.id, "Профиль успешно разморожен")


@registered_user_router.callback_query(
    ProfileAction.filter(F.action == ProfileOptions.return_to_main_menu))
async def return_to_main_menu(call: types.CallbackQuery, state: FSMContext, bot: Bot, dbpool):
    await bot.send_message(call.from_user.id, "Здравствуйте",
                           reply_markup=user_profile_keyboard)
    await state.set_state(state=None)
