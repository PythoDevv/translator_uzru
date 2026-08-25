# import asyncio
#
# from aiogram import types
# from aiogram.dispatcher import FSMContext
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
# from aiogram.utils import exceptions
#
# from data.config import ADMINS
# # from keyboards.default.all import menu
# from keyboards.default.admin import back, admin_key
# from loader import dp, db, bot
# from states.allStates import AllState
#
#
# @dp.message_handler(text='Xabar Yuborish 🗒', user_id=ADMINS)
# async def bot_start(msg: types.Message, state: FSMContext):
#     await msg.answer("<b>Xabarni ni yuboring</b>", reply_markup=back)
#     await AllState.post.set()
#
#
# @dp.message_handler(content_types=['video', 'audio', 'voice', 'photo', 'document', 'text'], user_id=ADMINS,
#                     state=AllState.post)
# async def contumum(msg: types.Message, state: FSMContext):
#     if msg.text == '🔙️ Orqaga':
#         await msg.answer('Bekor qilindi', reply_markup=admin_key)
#         await state.finish()
#
#     elif msg.video or msg.audio or msg.voice or msg.document or msg.photo or msg.text:
#
#         await state.finish()
#
#         users = await db.select_all_users()
#         count_baza = await db.count_users()
#         count_err = 0
#         count = 0
#         for user in users:
#             user_id = user[3]
#             try:
#                 await msg.send_copy(chat_id=user_id)
#                 count += 1
#                 await asyncio.sleep(0.05)
#
#             except Exception as err:
#                 count_err += 1
#                 await asyncio.sleep(0.05)
#
#         await msg.answer(f"Ҳабар юборилганлар: <b>{count}</b> та."
#                          f"\n\nЮборилмаганлар: <b>{count_err}</b> та."
#                          f"\n\nБазада жами: <b>{count_baza}</b> та"
#                          f" фойдаланувчи мавжуд.", reply_markup=admin_key
#                          )
