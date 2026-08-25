import asyncio
import os
import time
# import aioschedule as schedule
import json
from datetime import datetime

import dotenv
from aiogram import types, Bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.builtin import CommandStart, Command
from aiogram.utils.json import json
from translate import Translator
# from aiogram_bots_db import SqliteBotDb
from data.config import ADMINS
from keyboards.default.admin import admin_key, back
from loader import dp, db, bot
from states.allStates import AllState
from utils.misc import subscription
from apscheduler.schedulers.asyncio import AsyncIOScheduler


@dp.message_handler(commands='ruuz')
async def bot_start(message: types.Message):
    a = await db.update_users_from_lang(from_lang='ru', to_lang='uz', tg_id=message.from_user.id)
    await message.answer(
        'Hozir "Rus - O`zbek" tarjima holatidasiz. "O`zbek - Rus" holatiga o`tish uchun /uzru buyrug`ini tering.')


@dp.message_handler(commands='uzru')
async def bot_start(message: types.Message):
    a = await db.update_users_from_lang(from_lang='uz', to_lang='ru', tg_id=message.from_user.id)
    await message.answer(
        'Hozir "O`zbek - Rus" tarjima holatidasiz. "Rus - O`zbek" holatiga o`tish uchun /ruuz buyrug`ini bering.')


@dp.message_handler(CommandStart())
async def bot_start(message: types.Message):
    try:
        await db.add_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            type=1
        )
    except Exception as err:
        pass
    status = True
    all = await db.select_chanel()
    chanels = []
    url = []
    for i in all:
        chanels.append(i['chanelll'])
        url.append(i['url'])

    for channel in chanels:
        status *= await subscription.check(user_id=message.from_user.id,
                                           channel=f'{channel}')
    if status:
        await message.answer(
            'Hozir "O`zbek - Rus" holatidasiz. "Rus - O`zbek" holatiga o`tish uchun /ruuz buyrug`ini bering.')
        await db.update_users_from_lang(from_lang='uz', to_lang='ru', tg_id=message.from_user.id)
    else:
        button = types.InlineKeyboardMarkup(row_width=1, )
        counter = 0
        for i in url:
            counter += 1
            button.add(types.InlineKeyboardButton(f"{counter}-канал", url=f'https://t.me/{i}'))
        button.add(types.InlineKeyboardButton(text="Tekshirish", callback_data="check_subs"))
        await message.answer(f"👋 Assalomu alaykum {message.from_user.first_name}\n\n"
                             f"Botdan foydalanish uchun kanalga obuna bo'lishingiz kerak. Obuna bo'lgach pastdagi Tekshirish tugmasini bosing!",
                             reply_markup=button,
                             disable_web_page_preview=True)


# api123.35.78.69.136
@dp.callback_query_handler(text="check_subs")
async def checker(call: types.CallbackQuery, state: FSMContext):
    try:
        await db.add_user(
            telegram_id=call.message.from_user.id,
            username=call.message.from_user.username,
            full_name=call.message.from_user.full_name,
            type=1
        )
        await db.update_users_from_lang(from_lang='uz', to_lang='ru', tg_id=call.from_user.id)

    except Exception as err:
        pass

    await call.answer()
    result = str()
    result2 = str()
    status = True
    all = await db.select_chanel()
    chanels = []
    url = []
    for i in all:
        chanels.append(i['chanelll'])
        url.append(i['url'])
    for channel in chanels:
        status *= await subscription.check(user_id=call.from_user.id,
                                           channel=f'{channel}')
    if status:
        await call.message.edit_text(
            'Hozir "O`zbek - Rus" tarjima holatidasiz. "Rus - O`zbek" holatiga o`tish uchun /ruuz buyrug`ini bering.')
        await db.update_users_from_lang(from_lang='uz', to_lang='ru', tg_id=call.from_user.id)

    else:
        button = types.InlineKeyboardMarkup(row_width=1, )
        counter = 0
        for i in url:
            counter += 1
            button.add(types.InlineKeyboardButton(f"{counter}-канал", url=f'https://t.me/{i}'))
        button.add(types.InlineKeyboardButton(text="✅ Азо бўлдим", callback_data="check_subs"))

        await call.message.edit_text(f'🚫қуйидагиларга аъзо бўлинг. '
                                     f'Кейин "Аъзо бўлдим" тугмасини босинг🚫',
                                     reply_markup=button, )


activee = 0
blockk = 0


async def is_activeee():
    users = await db.select_all_users()
    global activee
    global blockk
    activate_test = 0
    blockk_test = 0
    # activee = 0
    # blockk = 0
    for user in users:

        user_id = user[3]
        try:
            await bot.send_chat_action(chat_id=user_id, action='typing')
            activate_test += 1
            await asyncio.sleep(0.034)

        except Exception as err:
            blockk_test += 1
            await asyncio.sleep(0.034)
    activee = activate_test
    blockk = blockk_test

@dp.message_handler(text='ttt')
async def is_activeee(a=None):
    users = await db.select_all_users()
    global activee
    global blockk
    activate_test = 0
    blockk_test = 0
    # activee = 0
    # blockk = 0
    for user in users:
        user_id = user[3]
        try:
            await bot.send_chat_action(chat_id=user_id, action='typing')
            activate_test += 1
            await asyncio.sleep(0.034)

        except Exception as err:
            blockk_test += 1
            await asyncio.sleep(0.034)
    activee = activate_test
    blockk = blockk_test


@dp.message_handler(content_types=[types.ContentType.NEW_CHAT_MEMBERS, types.ContentType.LEFT_CHAT_MEMBER])
async def user_joined_chat(message: types.Message):
    print('Users changed')


@dp.message_handler(text='Statistika 📊')
async def show_users(message: types.Message):
    a = await db.count_users()
    # active = await db.count_active_users()
    # block = await db.count_block_users()
    await message.answer(f'<b>🔷 Jami obunachilar: {a} tа</b>\n\n'
                         f'Active: {activee}\n'
                         f'Block: {blockk}')


admins = [1033990411, 935795577, 1604052132]


@dp.message_handler(text='Admin ➕')
async def add_channel(message: types.Message):
    global admins
    if message.from_user.id in admins:
        await message.answer('Id ni kiriting')
        await AllState.env.set()


@dp.message_handler(state=AllState.env)
async def env_change(message: types.Message, state: FSMContext):
    global admins
    try:
        # key = 'ADMINS'
        input_value = int(message.text)
        # dotenvfile = dotenv.find_dotenv()
        # dotenv.load_dotenv(dotenvfile)
        # old = dotenv.get_key(dotenv_path=dotenvfile, key_to_get='ADMINS')
        # value = f"{old},{input_value}"
        # os.environ[key] = value
        # dotenv.set_key(
        #     dotenvfile,
        #     key,
        #     os.environ[key]
        # )
        admins.append(int(message.text))
        # new = dotenv.get_key(dotenv_path=dotenvfile, key_to_get='ADMINS')
        await message.answer(f"Qo'shildi\n\n"
                             f"Hozirgi adminlar-{admins}", reply_markup=admin_key)
        await state.finish()
    except ValueError:
        await message.answer('Faqat son qabul qilinadi\n\n'
                             'Qaytadan kiriting')


@dp.message_handler(text='add')
async def add_channel(message: types.Message):
    global admins
    await message.answer(f'{admins}')


@dp.message_handler(text='Admin ➖')
async def add_channel(message: types.Message):
    global admins
    if message.from_user.id in admins:
        await message.answer('Id ni kiriting')
        await AllState.env_remove.set()


@dp.message_handler(state=AllState.env_remove)
async def env_change(message: types.Message, state: FSMContext):
    try:
        test = int(message.text)
        global admins
        # key = 'ADMINS'
        # dotenvfile = dotenv.find_dotenv()
        # dotenv.load_dotenv(dotenvfile)
        # old = dotenv.get_key(dotenv_path=dotenvfile, key_to_get='ADMINS')
        if test in admins:
            # a = ''
            # if f",{message.text}" in old:
            #     a += old.replace(f",{message.text}", '')
            # os.environ[key] = a
            # dotenv.set_key(
            #     dotenvfile,
            #     key,
            #     os.environ[key]
            # )
            admins.remove(test)
            # new = dotenv.get_key(dotenv_path=dotenvfile, key_to_get='ADMINS')
            await message.answer(f'O"chirildi\n\n'
                                 f'Hozirgi adminlar {admins}', reply_markup=admin_key)
            await state.finish()
        else:
            await message.answer('Bunday admin mavjud emas\n\n'
                                 'Faqat admin id sini qabul qilamiz', reply_markup=admin_key)
    except Exception as err:
        await message.answer(f'{err}')
        await message.answer('Faqat son qabul qilinadi\n\n'
                             'Qaytadan kiriting')


@dp.message_handler(text='Barcha Adminlar')
async def add_channel(message: types.Message):
    # dotenvfile = dotenv.find_dotenv()
    #
    # old = dotenv.get_key(dotenv_path=dotenvfile, key_to_get='ADMINS')
    global admins
    await message.answer(f'Adminlar - {admins}', reply_markup=admin_key)


@dp.message_handler(commands=['admin'])
async def admin(message: types.Message):
    global admins
    if message.from_user.id in admins:
        await message.answer(text='Admin panel',
                             reply_markup=admin_key)


@dp.message_handler(text='Kanal ➕')
async def add_channel(message: types.Message):
    global admins
    if message.from_user.id in admins:
        await message.answer(text='Kanalni kiriting\n\n'
                                  'Masalan : "@Chanel zayavkada bo`lsa chanel_id(-123123213),chanel_url"\n\n',
                             reply_markup=back)
        await AllState.add.set()


@dp.message_handler(state=AllState.add)
async def add_username(message: types.Message, state: FSMContext):
    text = message.text
    if text[0] == '@':
        await db.add_chanell(chanelll=f"{text}", url=f"{text[1:]}")
        await message.answer("Qo'shildi", reply_markup=admin_key)
        await state.finish()
    elif text == '🔙️ Orqaga':
        await message.answer('Admin panel', reply_markup=admin_key)
        await state.finish()
    elif text[0] == '-':
        split_chanel = message.text.split(',')
        chanel_lst = []
        url_lst = []
        for i in split_chanel:
            lst = i.split('and')
            chanel_lst.append(lst[0])
            url_lst.append(lst[1])
        chanel = f'{chanel_lst}'
        url = f'{url_lst}'
        ch_text = chanel.replace("'", '')
        ch_text2 = ch_text.replace(" ", '')
        u_text = url.replace("'", '')
        u_text2 = u_text.replace(" ", '')

        await db.add_chanell(chanelll=ch_text2[1:-1], url=u_text2[1:-1])
        await message.answer("Qo'shildi", reply_markup=admin_key)
        await state.finish()

    else:
        await message.answer('Xato\n\n'
                             '@ belgi bilan yoki kanal id(-11001835334270andLink) sini link bilan birga kiriting kiriting')


@dp.message_handler(text='Kanal ➖')
async def add_channel(message: types.Message):
    global admins
    if message.from_user.id in admins:
        await message.answer(text='Kanalni kiriting @ belgi bilan\n\n'
                                  'Masalan : "Kanal zayavkada bo`lsa chanel_id(-123123213),chanel_url"\n\n',
                             reply_markup=back)
        await AllState.delete.set()


@dp.message_handler(state=AllState.delete)
async def del_username(message: types.Message, state: FSMContext):
    txt = message.text
    if txt[0] == '-':
        chanel = await db.get_chanel(channel=txt)
        if not chanel:
            await message.answer("Kanal topilmadi\n"
                                 "Qaytadan urinib ko'ring")

        else:
            await db.delete_channel(chanel=txt)
            await message.answer('Kanal o"chirildi', reply_markup=admin_key)
            await state.finish()

        # await message.answer("O'chirildi")
        # await state.finish()
    elif txt[0] == '@':
        chanel = await db.get_chanel(channel=f"{txt}")
        if not chanel:
            await message.answer("Kanal topilmadi\n"
                                 "Qaytadan urinib ko'ring")

        else:
            await db.delete_channel(chanel=txt)
            await message.answer('Kanal o"chirildi', reply_markup=admin_key)
            await state.finish()
    elif txt == '🔙️ Orqaga':
        await message.answer('Admin panel', reply_markup=admin_key)
        await state.finish()


@dp.message_handler(text='🏘 Bosh menu')
async def menuu(message: types.Message):
    await message.answer('Bosh menu', reply_markup=admin_key)


@dp.message_handler(text='Kanallar 📈')
async def channels(message: types.Message):
    channels = await db.select_chanel()
    text = ''
    for channel in channels:
        text += f"{channel['chanelll']}\n"
    try:
        await message.answer(f"{text}", reply_markup=admin_key)
    except:
        await message.answer(f"Kanallar mavjud emas")


@dp.message_handler(text='Xabar Yuborish 🗒')
async def bot_start(msg: types.Message, state: FSMContext):
    global admins
    if msg.from_user.id in admins:
        await msg.answer("<b>Xabarni ni yuboring</b>", reply_markup=back)
        await AllState.post.set()


@dp.message_handler(content_types=['video', 'audio', 'voice', 'photo', 'document', 'text'],
                    state=AllState.post)
async def contumum(msg: types.Message, state: FSMContext):
    if msg.text == '🔙️ Orqaga':
        await msg.answer('Bekor qilindi', reply_markup=admin_key)
        await state.finish()

    elif msg.video or msg.audio or msg.voice or msg.document or msg.photo or msg.text:
        if msg.text == 'Xabar Yuborish 🗒':
            await msg.answer('Adashdingiz Shekilli\n\n'
                             'To`g`ri ma`lumot kirting')
        else:
            await state.finish()

            users = await db.select_all_users()
            count_baza = await db.count_users()
            count_err = 0
            count = 0
            for user in users:
                user_id = user[3]
                adminsss = [1033990411, 935795577, 1604052132]
                try:
                    await msg.send_copy(chat_id=user_id)
                    count += 1
                    await asyncio.sleep(0.05)
                except Exception as err:
                    count_err += 1
                    await asyncio.sleep(0.05)

            await msg.answer(f"Ҳабар юборилганлар: <b>{count}</b> та."
                             f"\n\nЮборилмаганлар: <b>{count_err}</b> та."
                             f"\n\nБазада жами: <b>{count_baza}</b> та"
                             f" фойдаланувчи мавжуд.", reply_markup=admin_key
                             )


@dp.message_handler(Command('jsonFile'))
async def jsonnn(message: types.Message):
    user_list = []
    userss = await db.select_all_users()
    for user in userss:
        user_dict = {}
        user_dict['full_name'] = user[1]
        user_dict['username'] = user[2]
        user_dict['phone'] = user[3]
        user_dict['score'] = user[4]
        user_dict['tg_id'] = user[6]
        user_list.append(user_dict)
        await asyncio.sleep(0.05)
    with open("users.json", "w") as outfile:
        json.dump(user_list, outfile)
    document = open('users.json')
    await bot.send_document(message.from_user.id, document=document)


async def jsonnnn():
    user_list = []
    userss = await db.select_all_users()
    for user in userss:
        user_dict = {}
        user_dict['full_name'] = user[1]
        user_dict['username'] = user[2]
        user_dict['phone'] = user[3]
        user_dict['score'] = user[4]
        user_dict['tg_id'] = user[6]
        user_list.append(user_dict)
        await asyncio.sleep(0.05)
    with open("users.json", "w") as outfile:
        json.dump(user_list, outfile)
    document = open('users.json')
    await bot.send_document(chat_id=935795577, document=document)


@dp.message_handler(Command('read_file'))
async def json_reader(message: types.Message):
    f = open('users.json', 'r')
    data = json.loads(f.read())
    for user in data:
        try:
            user = await db.add_json_file_user(
                telegram_id=user['tg_id'],
                username=user['username'],
                full_name=user['full_name'],
                phone=user['phone'],
                score=user['score']
            )
        except Exception as e:
            print(e)
    f.close()
