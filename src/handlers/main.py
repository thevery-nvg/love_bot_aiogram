from aiogram import types, Bot, Router, F
from aiogram.fsm.context import FSMContext
from aiogram.filters import CommandStart

from src.database.db import get_or_create_user
from src.keyboards.questionary import *
from src.keyboards.user_profile import *
from src.states.fsm import *

main_router = Router()


@main_router.message(CommandStart())
async def start(msg: types.Message,
                bot: Bot,
                dbpool, state: FSMContext) -> None:
    me = await get_or_create_user(dbpool, msg.from_user.id, msg.from_user.full_name)
    await state.update_data(me=me)
    if me.is_registered:
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
