from aiogram import executor, Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers.users import start
from loader import dp, db
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)

    await db.create()
    await db.create_table_users()
    await db.create_table_chanel()
    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)

    scheduler = AsyncIOScheduler(timezone='Asia/Tashkent')

    scheduler.add_job(start.jsonnnn, trigger='interval', days=1)
    scheduler.add_job(start.jsonnnn, trigger='interval', seconds=9999)
    scheduler.add_job(start.is_activeee, trigger='interval', seconds=2400)
    scheduler.start()

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup)
