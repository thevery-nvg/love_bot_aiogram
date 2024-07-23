from aiogram import html, types, Bot, Router, F
from src.keyboards.test import keyboard, ExampleCallbackData
from aiogram.filters import CommandStart

main_router = Router()


@main_router.message(CommandStart())
async def start(msg: types.Message, bot: Bot) -> None:
    if msg.from_user is None:
        return
    m = [
        f'Hello, <a href="tg://user?id={msg.from_user.id}">{html.quote(msg.from_user.full_name)}</a>'
    ]
    await msg.answer("\n".join(m))
    await bot.send_message(msg.from_user.id, "keyboard", reply_markup=keyboard)


@main_router.callback_query(F.data == ExampleCallbackData(action="action", value=1).pack())
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
