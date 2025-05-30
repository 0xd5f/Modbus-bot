from aiogram import Bot
from db import SessionLocal, User

async def notify_admins(bot: Bot, text: str):
    async with SessionLocal() as session:
        admins = (await session.execute(User.__table__.select().where(User.is_admin == True))).scalars().all()
        for admin in admins:
            await bot.send_message(admin.telegram_id, text)

async def notify_users(bot: Bot, text: str):
    async with SessionLocal() as session:
        users = (await session.execute(User.__table__.select().where(User.receive_notifications == True))).scalars().all()
        for user in users:
            await bot.send_message(user.telegram_id, text)
