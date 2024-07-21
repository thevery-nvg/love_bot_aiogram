import asyncio
import structlog
import tenacity

from aiogram import Dispatcher, Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.fsm.storage.base import DefaultKeyBuilder
from aiogram.fsm.storage.memory import MemoryStorage

from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

from sqlalchemy.ext.asyncio import AsyncSession

from src.data import config
from src.data.config import BOT_TOKEN, REDIS_STATUS
from src.middlewares.logging import StructLoggingMiddleware
from src.utils.logging import setup_logger
from src.utils.connect_to_services import wait_sqlalchemy, wait_redis_pool


async def create_db_connections(dp: Dispatcher) -> None:
    logger: structlog.typing.FilteringBoundLogger = dp["db_logger"]
    logger.debug("Connecting to SQLAlchemy[PostgreSQL]", db="main")
    try:
        db_pool = await wait_sqlalchemy(
            logger=dp["db_logger"],
        )
    except tenacity.RetryError:
        logger.error("Failed to connect to SQLAlchemy[PostgreSQL]", db="main")
        exit(1)
    else:
        logger.debug("Succesfully connected to SQLAlchemy[PostgreSQL]", db="main")
    dp["db_pool"] = db_pool

    if config.USE_CACHE:
        logger.debug("Connecting to Redis")
        try:
            redis_pool = await wait_redis_pool(
                logger=dp["cache_logger"],
                host=config.CACHE_HOST,
                password=config.CACHE_PASSWORD,
                port=config.CACHE_PORT,
                database=0,
            )
        except tenacity.RetryError:
            logger.error("Failed to connect to Redis")
            exit(1)
        else:
            logger.debug("Succesfully connected to Redis")
        dp["cache_pool"] = redis_pool


async def close_db_connections(dp: Dispatcher) -> None:
    if "temp_bot_cloud_session" in dp.workflow_data:
        temp_bot_cloud_session: AiohttpSession = dp["temp_bot_cloud_session"]
        await temp_bot_cloud_session.close()
    if "temp_bot_local_session" in dp.workflow_data:
        temp_bot_local_session: AiohttpSession = dp["temp_bot_local_session"]
        await temp_bot_local_session.close()
    if "db_pool" in dp.workflow_data:
        db_pool: AsyncSession = dp["db_pool"]
        await db_pool.close()
    if "cache_pool" in dp.workflow_data:
        cache_pool: redis.asyncio.Redis = dp["cache_pool"]  # type: ignore[type-arg]
        await cache_pool.close()


def setup_middlewares(dp: Dispatcher) -> None:
    dp.update.outer_middleware(StructLoggingMiddleware(logger=dp["aiogram_logger"]))


def setup_handlers(dp: Dispatcher) -> None:
    # dp.include_router()
    ...


def setup_logging(dp: Dispatcher) -> None:
    dp["aiogram_logger"] = setup_logger().bind(type="aiogram")
    dp["db_logger"] = setup_logger().bind(type="db")
    # dp["cache_logger"] = setup_logger().bind(type="cache")
    # dp["business_logger"] = setup_logger().bind(type="business")


async def setup_aiogram(dp: Dispatcher) -> None:
    setup_logging(dp)
    logger = dp["aiogram_logger"]
    logger.debug("Configuring aiogram")
    await create_db_connections(dp)
    setup_handlers(dp)
    setup_middlewares(dp)
    logger.info("Configured aiogram")


async def aiogram_on_startup_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    await bot.delete_webhook(drop_pending_updates=True)
    await setup_aiogram(dispatcher)
    dispatcher["aiogram_logger"].info("Started polling")


async def aiogram_on_shutdown_polling(dispatcher: Dispatcher, bot: Bot) -> None:
    dispatcher["aiogram_logger"].debug("Stopping polling")
    await close_db_connections(dispatcher)
    await bot.session.close()
    await dispatcher.storage.close()
    dispatcher["aiogram_logger"].info("Stopped polling")


def main() -> None:
    bot = Bot(BOT_TOKEN)
    if REDIS_STATUS:
        storage = MemoryStorage()
    else:
        storage = RedisStorage(
            redis=Redis(
                host=config.FSM_HOST,
                password=config.FSM_PASSWORD,
                port=config.FSM_PORT,
                db=0,
            ))
    dp = Dispatcher(key_builder=DefaultKeyBuilder(with_bot_id=True), storage=storage)
    aiogram_session_logger = setup_logger().bind(type="aiogram_session")
    dp["aiogram_session_logger"] = aiogram_session_logger
    dp.startup.register(aiogram_on_startup_polling)
    dp.shutdown.register(aiogram_on_shutdown_polling)
    asyncio.run(dp.start_polling(bot))


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Bot successfully stopped by keyboard")
