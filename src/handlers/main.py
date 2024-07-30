from aiogram import html, types, Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart
from src.database.db import add_user_if_not_exists, update_user
from src.keyboards.questionary import *
from src.database.models import Gender
from src.states.ddd import *

main_router = Router()


@main_router.message(CommandStart())
async def start(msg: types.Message, bot: Bot, db_pool) -> None:
    if msg.from_user is None:
        return
    m = [
        f'Hello, <a href="tg://user?id={msg.from_user.id}">{html.quote(msg.from_user.full_name)}</a>'
    ]
    await msg.answer("\n".join(m))
    await add_user_if_not_exists(db_pool,msg.from_user.id, msg.from_user.full_name)
    await bot.send_message(msg.from_user.id, "keyboard", reply_markup=register_keyboard)


@main_router.callback_query(QuestionAction.filter(F.question == Questions.register))
async def start_filling(call: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
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
async def ask_age(call: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await bot.send_message(call.from_user.id, "Введите ваш возраст")
    await state.set_state(Anketa.gender)


@main_router.message(Anketa.gender)
async def ask_gender(message: types.Message, state: FSMContext, bot: Bot) -> None:
    # Проверить является ли введенное значение числом
    age = message.text.strip()
    await state.update_data(age=age)
    await bot.send_message(message.from_user.id, "Выбирите ваш пол", reply_markup=gender_keyboard)
    await state.set_state(Anketa.looking_for)


@main_router.callback_query(QuestionAction.filter(F.question == Questions.gender_male),
                            QuestionAction.filter(F.question == Questions.gender_female),
                            Anketa.looking_for)
async def ask_looking_for(call: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if call.data == QuestionAction(question=Questions.gender_male).pack():
        await state.update_data(gender=Gender.male)
    elif call.data == QuestionAction(question=Questions.gender_female).pack():
        await state.update_data(gender=Gender.female)
    await bot.send_message(call.from_user.id, "Кого хотите найти",
                           reply_markup=looking_for_keyboard)
    await state.set_state(Anketa.location)


@main_router.callback_query(
    QuestionAction.filter(F.question == Questions.looking_for_male),
    QuestionAction.filter(F.question == Questions.looking_for_female),
    QuestionAction.filter(F.question == Questions.looking_for_anything),
    Anketa.location
)
async def ask_location(call: types.CallbackQuery, state: FSMContext, bot: Bot) -> None:
    if call.data == QuestionAction(question=Questions.looking_for_male).pack():
        await state.update_data(looking_for=Gender.male)
    elif call.data == QuestionAction(question=Questions.looking_for_female).pack():
        await state.update_data(looking_for=Gender.female)
    elif call.data == QuestionAction(question=Questions.looking_for_anything).pack():
        await state.update_data(looking_for=Gender.anything)
    await bot.send_message(call.from_user.id, "Отправьте ваше местоположение или напишите город",
                           reply_markup=get_location_keyboard)
    await state.set_state(Anketa.name)


@main_router.message(Anketa.name)
async def ask_name(message: types.Message, state: FSMContext, bot: Bot) -> None:
    # Проверить введены координаты или город
    # Если город, то проверить корректность ввода
    latitude = message.location.latitude
    longitude = message.location.longitude
    await state.update_data(longitude=longitude, latitude=latitude)
    await bot.send_message(message.from_user.id, "Ваше имя")
    await state.set_state(Anketa.description)


@main_router.message(Anketa.description)
async def ask_description(message: types.Message, state: FSMContext, bot: Bot) -> None:
    # Имя должно содержать только буквы
    await state.update_data(name=message.text.strip())
    await bot.send_message(message.from_user.id, "Расскажи о себе и кого хочешь найти,\n"
                                                 "чем предлагаешь заняться.\n"
                                                 "Это поможет лучше подобрать тебе кого-то")
    await state.set_state(Anketa.photo)


@main_router.message(Anketa.photo)
async def ask_photo(message: types.Message, state: FSMContext, bot: Bot) -> None:
    await state.update_data(description=message.text.strip())
    await bot.send_message(message.from_user.id, "Отправьте фото")
    await state.set_state(Anketa.done)
    await state.update_data(photo=[])


@main_router.message(Anketa.done, content_type="photo")
async def ask_photo(message: types.Message, state: FSMContext, bot: Bot) -> None:
    data = await state.get_data()
    photos = data.get("photo")
    photos.append(message.photo[-1].file_id)
    await state.update_data(photo=photos)
    if len(photos) == 1:
        msg = ("Ваша анкета заполнена, спасибо!\n"
               "Нажмите на кнопку для завершения\n"
               "Или отправьте еще фото")
    elif len(photos) == 2:
        msg = "Фото добавлено!Отправьте еще или нажмите на кнопку для завершения"
    else:
        msg = "Ваша анкета заполнена, спасибо!\nНажмите на кнопку для завершения"

    await bot.send_message(message.from_user.id, msg,
                           reply_markup=done_filling_keyboard)


@main_router.callback_query(QuestionAction.filter(F.question == Questions.done_filling),
                            Anketa.done)
async def done_filling(call: types.CallbackQuery, state: FSMContext, db_pool) -> None:
    # unfinished
    data = await state.get_data()
    age: int = data.get("age")
    gender: Gender = data.get("gender")
    looking_for: Gender = data.get("looking_for")
    name: str = data.get("name")
    description: str = data.get("description")
    photos: list[str] = data.get("photo")
    longitude: str = data.get("longitude")
    latitude: str = data.get("latitude")
    await update_user(db_pool,
                      user_id=call.from_user.id,
                      age=age,
                      gender=gender,
                      looking_for=looking_for,
                      name=name,
                      description=description,
                      photos=photos,
                      latitude=latitude,
                      longitude=longitude,
                      )
