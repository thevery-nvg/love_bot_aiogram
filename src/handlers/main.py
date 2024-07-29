from aiogram import html, types, Bot, Router, F, Dispatcher
from aiogram.fsm.context import FSMContext
from src.keyboards.test import keyboard, ExampleCallbackData, AdminAction, Action
from aiogram.filters import CommandStart
from src.database.db import add_user_if_not_exists

main_router = Router()


@main_router.message(CommandStart())
async def start(msg: types.Message, bot: Bot, db_pool) -> None:

    if msg.from_user is None:
        return
    m = [
        f'Hello, <a href="tg://user?id={msg.from_user.id}">{html.quote(msg.from_user.full_name)}</a>'
    ]

    await msg.answer("\n".join(m))
    await add_user_if_not_exists(msg.from_user.id, msg.from_user.full_name, db_pool)
    await bot.send_message(msg.from_user.id, "keyboard", reply_markup=keyboard)


@main_router.callback_query(AdminAction.filter(F.action == Action.ban), AdminAction.filter(
    F.value == 1))
async def ac1(msg: types.Message, bot: Bot) -> None:
    await bot.send_message(msg.from_user.id, "-----------BUTTON 1 Pressed-------------")


@main_router.callback_query(F.data == ExampleCallbackData(action="action", value=2).pack())
async def ac2(msg: types.Message, bot: Bot) -> None:
    await bot.send_message(msg.from_user.id, "-----------BUTTON 2 Pressed-------------")


@main_router.callback_query(F.data == ExampleCallbackData(action="action", value=3).pack())
async def ac3(msg: types.Message, bot: Bot) -> None:
    await bot.send_message(msg.from_user.id, "-----------BUTTON 3 Pressed-------------")


@main_router.callback_query(F.data == ExampleCallbackData(action="action", value=4).pack())
async def ac4(msg: types.Message, bot: Bot) -> None:
    await bot.send_message(msg.from_user.id, "-----------BUTTON 4 Pressed-------------")
