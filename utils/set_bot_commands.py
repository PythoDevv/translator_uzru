from aiogram import types


async def set_default_commands(dp):
    await dp.bot.set_my_commands(
        [
            types.BotCommand("start", "Botni ishga tushurish"),
            types.BotCommand("ruuz", "Rus - O'zbek"),
            types.BotCommand("uzru", "O'zbek - Rus"),
        ]
    )
