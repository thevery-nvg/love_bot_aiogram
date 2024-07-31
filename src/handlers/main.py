from aiogram import html, types, Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from src.database.db import get_or_create_user, update_user
from src.keyboards.questionary import *
from src.keyboards.user_profile import *
from src.database.models import Gender
from src.states.fsm import *
from src.utils.validators import *

main_router = Router()


@main_router.message(CommandStart())
async def start(msg: types.Message,
                bot: Bot,
                db_pool) -> None:
    user = await get_or_create_user(db_pool, msg.from_user.id, msg.from_user.full_name)
    if user.is_registered:
        if user.frozen:
            await bot.send_message(msg.from_user.id, "Здравствуйте",
                                   reply_markup=user_profile_keyboard_frozen)
        else:
            await bot.send_message(msg.from_user.id, "Здравствуйте",
                                   reply_markup=user_profile_keyboard)
    else:
        await bot.send_message(msg.from_user.id, "Здравствуйте", reply_markup=register_keyboard)


@main_router.callback_query(QuestionAction.filter(F.question == Questions.register))
async def start_filling(call: types.CallbackQuery,
                        state: FSMContext,
                        bot: Bot) -> None:
    await bot.send_message(call.from_user.id,
                           "Здравствуйте,вы начинаете заполнение анкеты,\n"
                           "Вам необходиму будет ответить на несколько вопросов,\n"
                           "Такие как:\n"
                           "Возраст\n"
                           "Пол\n"
                           "Кого хотите найти\n"
                           "Ваше расположение\n"
                           "Ваше имя\n"
                           "О себе\n"
                           "Фото(одно или несколько)\n",
                           reply_markup=start_filling_keyboard)
    await state.set_state(Anketa.age)


@main_router.callback_query(QuestionAction.filter(F.question == Questions.start), Anketa.age)
async def ask_age(call: types.CallbackQuery, bot: Bot) -> None:
    await bot.send_message(call.from_user.id, "Введите ваш возраст")


@main_router.message(Anketa.age)
async def receive_age_ask_gender(msg: types.Message,
                                 state: FSMContext,
                                 bot: Bot) -> None:
    if validate_age(msg.text):
        await state.update_data(age=int(msg.text.strip()))
        await bot.send_message(msg.from_user.id, "Выберите ваш пол", reply_markup=gender_keyboard)
        await state.set_state(Anketa.gender)
    else:
        await bot.send_message(msg.from_user.id, "Введите корректный возраст(число от 18 до 99)")


@main_router.callback_query(Anketa.gender)
async def receive_gender_ask_looking_for(call: types.CallbackQuery,
                                         state: FSMContext,
                                         bot: Bot) -> None:
    if call.data == QuestionAction(question=Questions.gender_male).pack():
        await state.update_data(gender=Gender.male)
    elif call.data == QuestionAction(question=Questions.gender_female).pack():
        await state.update_data(gender=Gender.female)
    await bot.send_message(call.from_user.id, "Кого хотите найти?",
                           reply_markup=looking_for_keyboard)
    await state.set_state(Anketa.looking_for)


@main_router.callback_query(Anketa.looking_for)
async def receive_looking_for_ask_location(call: types.CallbackQuery,
                                           state: FSMContext,
                                           bot: Bot) -> None:
    if call.data == QuestionAction(question=Questions.looking_for_male).pack():
        await state.update_data(looking_for=Gender.male)
    elif call.data == QuestionAction(question=Questions.looking_for_female).pack():
        await state.update_data(looking_for=Gender.female)
    elif call.data == QuestionAction(question=Questions.looking_for_anything).pack():
        await state.update_data(looking_for=Gender.anything)
    await bot.send_message(call.from_user.id, "Отправьте ваше местоположение или напишите город",
                           reply_markup=get_location_keyboard)
    await state.set_state(Anketa.location)


@main_router.message(Anketa.location)
async def receive_location_ask_name(message: types.Message,
                                    state: FSMContext,
                                    bot: Bot) -> None:
    if message.location is not None:
        latitude = message.location.latitude
        longitude = message.location.longitude
        await state.update_data(longitude=longitude, latitude=latitude)
    else:
        city = message.text.strip()
        if validate_city(city):
            await state.update_data(city=city)
            await bot.send_message(message.from_user.id, "Ваше имя")
            await state.set_state(Anketa.name)
        else:
            await bot.send_message(message.from_user.id, "Введите корректный город")
            await state.update_data(city=city)


@main_router.message(Anketa.name)
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


@main_router.message(Anketa.description)
async def receive_desc_ask_photo(message: types.Message,
                                 state: FSMContext,
                                 bot: Bot) -> None:
    await state.update_data(description=message.text.strip())
    await bot.send_message(message.from_user.id, "Отправьте фото")
    await state.set_state(Anketa.photo)
    await state.update_data(photos=[])


@main_router.message(Anketa.photo, content_type="photo")
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


@main_router.message(Anketa.photo)
async def invalid_photo(message: types.Message,
                        bot: Bot) -> None:
    await bot.send_message(message.from_user.id, "Отправьте только фото")


@main_router.callback_query(QuestionAction.filter(F.question == Questions.done_filling))
async def done_filling(call: types.CallbackQuery,
                       state: FSMContext,
                       db_pool) -> None:
    # unfinished
    data = await state.get_data()
    profile = dict()
    profile["age"]: int = data.get("age")
    profile["gender"]: Gender = data.get("gender")
    profile["looking_for"]: Gender = data.get("looking_for")
    profile["name"]: str = data.get("name")
    profile["description"]: str = data.get("description")
    profile["photos"]: list[str] = data.get("photos")
    longitude: str = data.get("longitude", None)
    latitude: str = data.get("latitude", None)
    if longitude is not None and latitude is not None:
        profile["longitude"]: float = float(longitude)
        profile["latitude"]: float = float(latitude)
    else:
        profile["city"] = data.get("city")
    await update_user(db_pool, user_id=call.from_user.id, **profile)
