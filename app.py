from aiogram import executor, Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from handlers.users import start
from loader import dp, db
import middlewares, filters, handlers
from utils.notify_admins import on_startup_notify
from utils.set_bot_commands import set_default_commands
from utils.misc.translation import close_translation_service
from data.config import ADMINS


async def on_startup(dispatcher):
    await set_default_commands(dispatcher)

    await db.create()
    await db.create_table_users()
    await db.create_table_chanel()
    await db.create_table_admins()
    await db.seed_admins(ADMINS)
    # Bot ishga tushgani haqida adminga xabar berish
    await on_startup_notify(dispatcher)

    scheduler = AsyncIOScheduler(timezone='Asia/Tashkent')

    # Bir xil backup jobi oldin ikki marta ishga tushardi va har 40 daqiqada
    # barcha foydalanuvchiga so'rov yuborilardi. Bu Telegram limitlariga olib keladi.
    scheduler.add_job(start.jsonnnn, trigger='interval', days=1, max_instances=1, coalesce=True)
    scheduler.start()


async def on_shutdown(dispatcher):
    await close_translation_service()
    if db.pool:
        await db.pool.close()

if __name__ == '__main__':
    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
