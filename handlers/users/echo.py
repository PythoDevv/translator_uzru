import html
import logging

from aiogram import types

from loader import db, dp
from utils.misc import subscription
from utils.misc.translation import TranslationError, translate_text


async def _is_subscribed(user_id: int) -> bool:
    for channel in await db.select_chanel():
        try:
            if not await subscription.check(user_id=user_id, channel=channel['chanelll']):
                return False
        except Exception:
            logging.exception("Subscription check failed for channel %s", channel['chanelll'])
            return False
    return True


async def _answer_translated(message: types.Message, text: str) -> None:
    # Telegram bir xabarda 4096 belgidan ortig'ini yubormaydi.
    for offset in range(0, len(text), 4096):
        await message.answer(html.escape(text[offset:offset + 4096]))


@dp.message_handler(state=None)
async def bot_echo(message: types.Message):
    await db.add_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        full_name=message.from_user.full_name,
        type=1,
    )
    channels = await db.select_chanel()
    if await _is_subscribed(message.from_user.id):
        try:
            lang = await db.select_user(telegram_id=message.from_user.id)
            translated = await translate_text(message.text, lang['from_lang'] or 'uz', lang['to_lang'] or 'ru')
            await _answer_translated(message, translated)
        except ValueError as error:
            await message.answer(str(error))
        except TranslationError:
            logging.exception('Translation request failed')
            await message.answer('Tarjima xizmati vaqtincha band. Bir ozdan keyin qayta urinib ko`ring.')
        except Exception:
            logging.exception('Unexpected translation request failure')
            await message.answer('Xatolik yuz berdi. Iltimos, /start buyrug`ini yuborib qayta urinib ko`ring.')
        return

    button = types.InlineKeyboardMarkup(row_width=1)
    for counter, channel in enumerate(channels, start=1):
        button.add(types.InlineKeyboardButton(f"{counter}-kanal", url=f"https://t.me/{channel['url']}"))
    button.add(types.InlineKeyboardButton(text="Tekshirish", callback_data="check_subs"))
    await message.answer(
        f"Assalomu alaykum {message.from_user.first_name}\n\n"
        "Botdan foydalanish uchun kanalga obuna bo'lishingiz kerak. "
        "Obuna bo'lgach pastdagi Tekshirish tugmasini bosing!",
        reply_markup=button,
        disable_web_page_preview=True,
    )
