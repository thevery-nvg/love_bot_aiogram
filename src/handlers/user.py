from aiogram import types, Bot, Router, F
from aiogram.fsm.context import FSMContext

from src.database.db import update_location
from src.keyboards.questionary import get_location_keyboard
from src.keyboards.user_profile import *
from src.states.fsm import Anketa
from src.utils.validators import validate_city

registered_user_router = Router()


@registered_user_router.callback_query(ProfileAction.filter(F.action == ProfileOptions.view_people))
async def view_people(call: types.CallbackQuery, state: FSMContext, bot: Bot, dbpool):
    ...


@registered_user_router.callback_query(
    ProfileAction.filter(F.action == ProfileOptions.like))
async def like(call: types.CallbackQuery, state: FSMContext, bot: Bot, dbpool):
    ...


@registered_user_router.callback_query(
    ProfileAction.filter(F.action == ProfileOptions.dislike))
async def dislike(call: types.CallbackQuery, state: FSMContext, bot: Bot, dbpool):
    ...


@registered_user_router.callback_query(
    ProfileAction.filter(F.action == ProfileOptions.unfreeze_profile))
async def view_my_profile(call: types.CallbackQuery, state: FSMContext, bot: Bot, dbpool):
    ...


@registered_user_router.callback_query(
    ProfileAction.filter(F.action == ProfileOptions.update_location))
async def refresh_location(call: types.CallbackQuery, state: FSMContext, bot: Bot):
    await bot.send_message(call.from_user.id, "Отправьте ваше местоположение или напишите город",
                           reply_markup=get_location_keyboard)
    await state.set_state(Anketa.location)


@registered_user_router.message(Anketa.location)
async def receive_location(message: types.Message,
                           bot: Bot,
                           dbpool,
                           state: FSMContext) -> None:
    if message.location is not None:
        latitude = message.location.latitude
        longitude = message.location.longitude
        await update_location(session=dbpool,
                              user_id=message.from_user.id,
                              latitude=latitude,
                              longitude=longitude)
        await state.clear()
    else:
        city = message.text.strip()
        if validate_city(city):
            await update_location(dbpool, message.from_user.id, city=city)
            await state.clear()
        else:
            await bot.send_message(message.from_user.id, "Введите корректный город")


@registered_user_router.callback_query(
    ProfileAction.filter(F.action == ProfileOptions.refill_profile))
async def refill_profile(call: types.CallbackQuery, state: FSMContext, bot: Bot, dbpool):
    ...


@registered_user_router.callback_query(
    ProfileAction.filter(F.action == ProfileOptions.freeze_profile))
async def freeze_profile(call: types.CallbackQuery, state: FSMContext, bot: Bot, dbpool):
    ...


@registered_user_router.callback_query(
    ProfileAction.filter(F.action == ProfileOptions.unfreeze_profile))
async def unfreeze_profile(call: types.CallbackQuery, state: FSMContext, bot: Bot, dbpool):
    ...


@registered_user_router.callback_query(
    ProfileAction.filter(F.action == ProfileOptions.unfreeze_profile))
async def return_to_main_menu(call: types.CallbackQuery, state: FSMContext, bot: Bot, dbpool):
    ...