from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

storage = MemoryStorage()
bot = Bot(Config.TG_TOKEN)
dp = Dispatcher(bot=bot, storage=storage)
