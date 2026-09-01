import logging

from aiogram import Dispatcher

async def on_startup_notify(dp: Dispatcher):
    # Import shu yerda qilinadi: loader -> utils import siklini oldini oladi.
    from loader import db

    for admin in await db.select_admins():
        try:
            await dp.bot.send_message(admin['telegram_id'], "Bot ishga tushdi.")
        except Exception as err:
            logging.warning("Startup notification could not be sent to %s: %s", admin['telegram_id'], err)
