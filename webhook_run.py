import asyncio
from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI, Request
from src.data.config import *
from src.run import close_db_connections
from src.utils.logging import setup_logger
from redis.asyncio import Redis
from aiogram.fsm.storage.redis import RedisStorage
import orjson
from dataclasses import dataclass, field

from src.utils.smart_session import SmartAiogramAiohttpSession
import aiojobs

app = FastAPI()
####################### ПРИМЕР СОЗДАНИЯ ФОНОВОЙ ЗАДАЧИ #######################
scheduler = None


async def send_message(chat_id: int, text: str):
    bot: Bot = bot_state.bot
    await bot.send_message(chat_id, text)


async def on_db_change():
    # Здесь  логика для определения изменений в базе данных
    chat_id = 123456789
    message_text = "Запись в базе данных изменилась!"
    await send_message(chat_id, message_text)


async def background_task():
    while True:
        await on_db_change()
        await asyncio.sleep(60)  # Проверять каждую минуту


####################### ПРИМЕР СОЗДАНИЯ ФОНОВОЙ ЗАДАЧИ #######################

@dataclass
class BotState:
    # TODO: Вот так нельзя, нужно что то придумать
    bot: Bot = field(default=None)
    dp: Dispatcher = field(default=None)


bot_state = BotState()


async def setup_aiogram(dp: Dispatcher) -> None:
    setup_logging(dp)
    logger = dp["aiogram_logger"]
    logger.debug("Configuring aiogram")
    await create_db_connections(dp)
    setup_handlers(dp)
    setup_middlewares(dp)
    logger.info("Configured aiogram")


@app.on_event("startup")
async def on_startup() -> None:
    global scheduler  ###
    aiogram_session_logger = setup_logger().bind(type="aiogram_session")
    session = SmartAiogramAiohttpSession(
        json_loads=orjson.loads,
        logger=aiogram_session_logger,
    )
    bot = Bot(token=BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode='HTML'))
    if REDIS_STATUS:
        storage = MemoryStorage()
    else:
        storage = RedisStorage(
            redis=Redis(
                host=FSM_HOST,
                password=FSM_PASSWORD,
                port=FSM_PORT,
                db=0,
            ))
    dp = Dispatcher(key_builder=DefaultKeyBuilder(with_bot_id=True), storage=storage)
    aiogram_session_logger = setup_logger().bind(type="aiogram_session")
    dp["aiogram_session_logger"] = aiogram_session_logger
    dp.startup.register(aiogram_on_startup_webhook)
    dp.shutdown.register(aiogram_on_shutdown_webhook)

    # Регистрация промежуточного слоя логирования
    # dp.update.outer_middleware(StructLoggingMiddleware(logger=dp["aiogram_logger"]))
    bot_state.bot = bot
    bot_state.dp = dp
    await dp.emit_startup()

    ######## Создание планировщика ##########
    scheduler = await aiojobs.create_scheduler()
    ######## Запуск фоновой задачи ##########
    await scheduler.spawn(background_task())


@app.on_event("shutdown")
async def on_shutdown() -> None:
    global scheduler  #############
    dp: Dispatcher = bot_state.dp
    await dp.emit_shutdown()
    await close_db_connections(dp)
    await dp.storage.close()
    await bot_state.bot.session.close()
    ####### Остановка планировщика #############
    if scheduler:
        await scheduler.close()


@app.post("/tg/webhooks/{token}/")
async def telegram_webhook(request: Request, token: str):
    if token != BOT_TOKEN:
        return {"status": "invalid token"}
    update = await request.json()
    bot: Bot = bot_state.bot
    dp: Dispatcher = bot_state.dp
    await dp.feed_update(bot=bot, update=update)  # тут большой вопрос, может и другая функция
    return {"status": "ok"}


async def aiogram_on_startup_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    await setup_aiogram(dispatcher)
    webhook_logger = dispatcher["aiogram_logger"].bind(webhook_url=MAIN_WEBHOOK_ADDRESS)
    webhook_logger.debug("Configuring webhook")
    await bot.set_webhook(
        url=MAIN_WEBHOOK_ADDRESS.format(token=BOT_TOKEN, bot_id=BOT_TOKEN.split(":")[0]),
        allowed_updates=dispatcher.resolve_used_update_types(),
        secret_token=MAIN_WEBHOOK_SECRET_TOKEN,
    )
    webhook_logger.info("Configured webhook")


async def aiogram_on_shutdown_webhook(dispatcher: Dispatcher, bot: Bot) -> None:
    dispatcher["aiogram_logger"].debug("Stopping webhook")
    await bot.delete_webhook()
    await close_db_connections(dispatcher)
    await dispatcher.storage.close()
    await bot.session.close()
    dispatcher["aiogram_logger"].info("Stopped webhook")


def main() -> None:
    import uvicorn
    uvicorn.run(
        "main:app",
        host=MAIN_WEBHOOK_LISTENING_HOST,
        port=MAIN_WEBHOOK_LISTENING_PORT,
        log_level="info",
        reload=True
    )


if __name__ == "__main__":
    main()
