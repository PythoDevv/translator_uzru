from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

back = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='🔙️ Orqaga'),
        ]
    ],
    resize_keyboard=True
)


admin_key = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Xabar Yuborish 🗒 '),
        ],
        [
            KeyboardButton(text='Barcha Adminlar'),
            KeyboardButton(text='Admin ➕'),
            KeyboardButton(text='Admin ➖')

        ],
        [
            KeyboardButton(text='Kanal ➕'),
            KeyboardButton(text='Kanal ➖')
        ],
        [
            KeyboardButton(text="Kanallar 📈"),
            KeyboardButton(text="Statistika 📊")
        ],
        [
            KeyboardButton(text="🏘 Bosh menu")

        ]
    ],
    resize_keyboard=True
)
