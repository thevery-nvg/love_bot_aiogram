from aiogram import Dispatcher, Bot
from aiogram.client.default import DefaultBotProperties
from aiogram.fsm.storage.memory import MemoryStorage
from fastapi import FastAPI, Request
from src.data.config import *
from src.run_polling import close_db_connections
from src.utils.logging import setup_logger
from redis.asyncio import Redis
from aiogram.fsm.storage.redis import RedisStorage
import orjson
from dataclasses import dataclass, field

from src.utils.smart_session import SmartAiogramAiohttpSession
import aiojobs
from src.run_polling import setup_aiogram

app = FastAPI()


@dataclass
class BotState:
    bot: Bot = field(default=None)
    dp: Dispatcher = field(default=None)
    scheduler: aiojobs.Scheduler = field(default=None)


bot_state = BotState()


@app.on_event("startup")
async def on_startup() -> None:
    aiogram_session_logger = setup_logger().bind(type="aiogram_session")
    session = SmartAiogramAiohttpSession(
        json_loads=orjson.loads,
        logger=aiogram_session_logger,
    )
    bot = Bot(token=BOT_TOKEN, session=session, default=DefaultBotProperties(parse_mode='HTML'))
    if not REDIS_FSM_ON:
        storage = MemoryStorage()
    else:
        storage = RedisStorage(
            redis=Redis(
                host=FSM_HOST,
                password=FSM_PASSWORD,
                port=FSM_PORT,
                db=0,
            ))
    dp = Dispatcher(bot=bot, storage=storage)
    aiogram_session_logger = setup_logger().bind(type="aiogram_session")
    dp["aiogram_session_logger"] = aiogram_session_logger

    dp.startup.register(aiogram_on_startup_webhook)
    dp.shutdown.register(aiogram_on_shutdown_webhook)


    bot_state.bot = bot
    bot_state.dp = dp
    bot_state.scheduler = aiojobs.Scheduler()

    await dp.emit_startup()

    # await bot_state.scheduler.spawn(background_task())


@app.on_event("shutdown")
async def on_shutdown() -> None:
    dp: Dispatcher = bot_state.dp
    await dp.emit_shutdown()
    await close_db_connections(dp)
    await dp.storage.close()
    await bot_state.bot.session.close()
    # Остановка планировщика
    # if bot_state.scheduler:
    #    await bot_state.scheduler.close()


@app.post(f"{MAIN_WEBHOOK_ADDRESS}/{BOT_TOKEN}")
async def telegram_webhook(request: Request, token: str):
    if token != BOT_TOKEN:
        return {"status": "invalid token"}
    update = await request.json()
    bot: Bot = bot_state.bot
    dp: Dispatcher = bot_state.dp
    await dp.feed_update(bot=bot, update=update)
    return {"status": "ok"}


async def aiogram_on_startup_webhook() -> None:
    dispatcher = bot_state.dp
    bot = bot_state.bot
    await setup_aiogram(dispatcher)
    webhook_logger = dispatcher["aiogram_logger"].bind(webhook_url=MAIN_WEBHOOK_ADDRESS)
    webhook_logger.debug("Configuring webhook")
    await bot.set_webhook(
        url=f"{MAIN_WEBHOOK_ADDRESS}/{BOT_TOKEN}",
        allowed_updates=dispatcher.resolve_used_update_types(),
        secret_token=MAIN_WEBHOOK_SECRET_TOKEN,
    )
    webhook_logger.info("Configured webhook")


async def aiogram_on_shutdown_webhook() -> None:
    dispatcher = bot_state.dp
    bot = bot_state.bot
    dispatcher["aiogram_logger"].debug("Stopping webhook")
    await bot.delete_webhook()
    await close_db_connections(dispatcher)
    await dispatcher.storage.close()
    await bot.session.close()
    dispatcher["aiogram_logger"].info("Stopped webhook")


def main() -> None:
    import uvicorn
    uvicorn.run(
        "__main__:app",
        host=MAIN_WEBHOOK_LISTENING_HOST,
        port=MAIN_WEBHOOK_LISTENING_PORT,
        log_level="info",
        reload=True
    )


if __name__ == "__main__":
    main()
