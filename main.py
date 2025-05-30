from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode, BotCommand
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio
from db import init_db
from bot.handlers import register_handlers
from scheduler import start_polling

API_TOKEN = "TOKEN_HERE"

async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="start", description="Справка и меню"),
        BotCommand(command="add_sensor", description="Добавить датчик"),
        BotCommand(command="calibrate", description="Калибровка датчика"),
        BotCommand(command="logs", description="График температуры"),
        BotCommand(command="block", description="Блокировать уведомления"),
        BotCommand(command="sensors", description="Список всех датчиков"),
    ]
    await bot.set_my_commands(commands)

async def main():
    await init_db()
    bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
    await set_commands(bot)
    dp = Dispatcher(bot, storage=MemoryStorage())
    scheduler = AsyncIOScheduler()
    register_handlers(dp, scheduler)
    start_polling(scheduler, bot)
    scheduler.start()
    await dp.start_polling()

if __name__ == "__main__":
    asyncio.run(main())
