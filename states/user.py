from aiogram.dispatcher.filters.state import State, StatesGroup


class Dispatch(StatesGroup):
    user_settings = State()
    user_waiting_for_subject_id = State()
    user_waiting_for_variant_answer = State()
    user_blocked = State()
    user_block_answer = State()