from aiogram import types
from googletrans import Translator
from loader import db, dp
from utils.misc import subscription


@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
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
        try:
            langs = await db.get_from(tg_id=message.from_user.id)
            from_lang = ''
            to_lang = ''
            for i in langs:
                from_lang += f"{i[0]}"
                to_lang += f"{i[1]}"
            tar = Translator()
            a = tar.translate(f'{message.text}', src=f'{from_lang}', dest=f'{to_lang}').text
            await message.answer(text=a)
        except:
            await message.answer('Kechirasiz faqat 500 tagacha bo`lgan so`zlarni qabul qilamiz\n\n'
                                 'Iltomos 500 tadan ortig`ini alohida kiriting\n\n'
                                 'Agar sizda boshqa muammo yuzaga kelgan bo`lsa iltimos /start buyrug`ini yuboring')

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
    try:
        await db.add_user(
            telegram_id=message.from_user.id,
            username=message.from_user.username,
            full_name=message.from_user.full_name,
            type=1
        )
        await db.update_users_from_lang(from_lang='uz', to_lang='ru', tg_id=message.from_user.id)

    except Exception as err:
        pass
