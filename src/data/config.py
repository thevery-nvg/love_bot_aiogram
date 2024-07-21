from environs import Env

env = Env()
env.read_env(path="D:\\Python\\love_bot_aiogram\\.env.dist")
BOT_TOKEN: str = env.str("BOT_TOKEN")
LOGGING_LEVEL: int = env.int("LOGGING_LEVEL", 10)

PG_HOST: str = env.str("PG_HOST")
PG_PORT: int = env.int("PG_PORT")
PG_USER: str = env.str("PG_USER")
PG_PASSWORD: str = env.str("PG_PASSWORD")
PG_DATABASE: str = env.str("PG_DATABASE")

USE_CACHE: bool = env.bool("USE_CACHE", False)
if USE_CACHE:
    CACHE_HOST: str = env.str("CACHE_HOST")
    CACHE_PORT: int = env.int("CACHE_PORT")
    CACHE_PASSWORD: str = env.str("CACHE_PASSWORD")

FSM_HOST: str = env.str("FSM_HOST")
FSM_PORT: int = env.int("FSM_PORT")
FSM_PASSWORD: str = env.str("FSM_PASSWORD")
REDIS_STATUS: bool = env.bool("REDIS_STATUS",False)
