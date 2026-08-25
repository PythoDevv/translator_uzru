# import os
# from aiogram import Bot, Dispatcher, types
# from aiogram.contrib.fsm_storage.memory import MemoryStorage
# from aiogram.dispatcher import FSMContext
# from aiogram.dispatcher.filters import Command
# from aiogram.types import ParseMode
# from aiogram.bot import SqliteBotDb
#
# # Bot tokenini olamiz
# API_TOKEN = os.getenv('API_TOKEN')
#
# # Bot obyektini yaratamiz
# bot = Bot(token='5439692016:AAGvhyZKIpHS1WboQxKQY5tNDtks_e7i2No')
#
# # Dispatcher obyektini yaratamiz
# dp = Dispatcher(bot, storage=MemoryStorage())
#
# # DB obyektini yaratamiz
# db = SqliteBotDb()
#
# # DB obyektini ishga tushiramiz
# db.init_db()
#
# # Foydalanuvchilar haqida ma'lumotni chiqaruvchi funksiya
# async def show_active_users(message: types.Message):
#     users = db.get_users(active=True)
#     chat_ids = [str(user["chat_id"]) for user in users]
#     await message.answer(f"Aktiv foydalanuvchilar soni: {len(chat_ids)}. Chat ID lar: {', '.join(chat_ids)}", parse_mode=ParseMode.HTML)
#
# # Komandalar qo'shamiz
# dp.register_message_handler(show_active_users, Command("active_users"))
#
# # Kodni ishga tushiramiz
# if name == 'main':
#     from aiogram import executor
#     executor.start_polling(dp, skip_updates=True)