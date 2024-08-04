from aiogram import types, Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Location

from src.database.db import update_user
from src.keyboards.questionary import *
from src.database.models import Gender
from src.keyboards.user_profile import user_profile_keyboard
from src.states.fsm import *
from src.utils.validators import *

register_router = Router()


@register_router.callback_query(QuestionAction.filter(F.question == Questions.start), Anketa.age)
async def ask_age(call: types.CallbackQuery, bot: Bot) -> None:
    await bot.send_message(call.from_user.id, "Введите ваш возраст")


@register_router.message(Anketa.age)
async def receive_age_ask_gender(msg: types.Message,
                                 state: FSMContext,
                                 bot: Bot) -> None:
    if validate_age(msg.text):
        await state.update_data(age=int(msg.text.strip()))
        await bot.send_message(msg.from_user.id, "Выберите ваш пол", reply_markup=gender_keyboard)
        await state.set_state(Anketa.gender)
    else:
        await bot.send_message(msg.from_user.id, "Введите корректный возраст(число от 18 до 99)")


@register_router.callback_query(Anketa.gender)
async def receive_gender_ask_looking_for(call: types.CallbackQuery,
                                         state: FSMContext,
                                         bot: Bot) -> None:
    if call.data == QuestionAction(question=Questions.gender_male, value=1).pack():
        await state.update_data(gender=Gender.male)
    elif call.data == QuestionAction(question=Questions.gender_female, value=1).pack():
        await state.update_data(gender=Gender.female)
    await bot.send_message(call.from_user.id, "Кого хотите найти?",
                           reply_markup=looking_for_keyboard)
    await state.set_state(Anketa.looking_for)


@register_router.callback_query(Anketa.looking_for)
async def receive_looking_for_ask_location(call: types.CallbackQuery,
                                           state: FSMContext,
                                           bot: Bot) -> None:
    if call.data == QuestionAction(question=Questions.looking_for_male, value=1).pack():
        await state.update_data(looking_for=Gender.male)
    elif call.data == QuestionAction(question=Questions.looking_for_female, value=1).pack():
        await state.update_data(looking_for=Gender.female)
    elif call.data == QuestionAction(question=Questions.looking_for_anything, value=1).pack():
        await state.update_data(looking_for=Gender.anything)
    await bot.send_message(call.from_user.id, "Отправьте ваше местоположение или напишите город",
                           reply_markup=get_location_keyboard)
    await state.set_state(Anketa.location)


@register_router.message(Anketa.location)
async def receive_location_ask_name(message: types.Message,
                                    state: FSMContext,
                                    bot: Bot) -> None:
    if message.location is not None:
        location: Location = message.location
        await state.update_data(location=location)
        await bot.send_message(message.from_user.id, "Ваше имя")
        await state.set_state(Anketa.name)
    else:
        city = message.text.strip()
        if validate_city(city):
            await state.update_data(city=city)
            await bot.send_message(message.from_user.id, "Ваше имя")
            await state.set_state(Anketa.name)
        else:
            await bot.send_message(message.from_user.id, "Введите корректный город")


@register_router.message(Anketa.name)
async def receive_name_ask_description(message: types.Message,
                                       state: FSMContext,
                                       bot: Bot) -> None:
    if validate_name(message.text):
        await state.update_data(name=message.text.strip())
        await bot.send_message(message.from_user.id, "О себе и кого хочешь найти,\n"
                                                     "чем предлагаешь заняться.\n"
                                                     "Это поможет лучше подобрать тебе кого-то")
        await state.set_state(Anketa.description)
    else:
        await bot.send_message(message.from_user.id, "Введите корректное имя")


@register_router.message(Anketa.description)
async def receive_desc_ask_photo(message: types.Message,
                                 state: FSMContext,
                                 bot: Bot) -> None:
    await state.update_data(description=message.text.strip())
    await bot.send_message(message.from_user.id, "Отправьте фото")
    await state.set_state(Anketa.photo)
    await state.update_data(photos=[])


@register_router.message(Anketa.photo, F.content_type == "photo")
async def receive_photo(message: types.Message,
                        state: FSMContext,
                        bot: Bot) -> None:
    data = await state.get_data()
    photos = data.get("photos")
    photos.append(message.photo[-1].file_id)
    await state.update_data(photos=photos)
    if len(photos) == 1:
        msg = ("Ваша анкета заполнена, спасибо!\n"
               "Нажмите на кнопку для завершения\n"
               "Или отправьте еще фото")
    elif len(photos) == 2:
        msg = "Фото добавлено!Отправьте еще или нажмите на кнопку для завершения"
    else:
        msg = "Ваша анкета заполнена, спасибо!\nНажмите на кнопку для завершения"
    await bot.send_message(message.from_user.id, msg, reply_markup=done_filling_keyboard)


@register_router.message(Anketa.photo)
async def invalid_photo(message: types.Message,
                        bot: Bot) -> None:
    await bot.send_message(message.from_user.id, "Отправьте только фото")


@register_router.callback_query(QuestionAction.filter(F.question == Questions.done_filling))
async def done_filling(call: types.CallbackQuery,
                       state: FSMContext,
                       bot: Bot,
                       db_pool) -> None:
    data = await state.get_data()
    profile = dict()
    profile["age"]: int = data.get("age")
    profile["gender"]: Gender = data.get("gender")
    profile["looking_for"]: Gender = data.get("looking_for")
    profile["name"]: str = data.get("name")
    profile["description"]: str = data.get("description")
    profile["photos"]: list[str] = data.get("photos")
    profile["is_registered"] = True
    location = data.get("location", None)
    if location is not None:
        profile["location"] = location
    else:
        profile["city"] = data.get("city")
    await update_user(db_pool, data.get('me'), **profile)
    await bot.send_message(call.from_user.id, "Здравствуйте", user_profile_keyboard)
    await state.set_state(state=None)
