from aiogram.dispatcher.filters.state import StatesGroup, State


class AllState(StatesGroup):
    post = State()
    add = State()
    delete = State()
    first = State()
    env = State()
    env_remove = State()
