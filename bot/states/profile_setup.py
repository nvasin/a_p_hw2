from aiogram.fsm.state import State, StatesGroup

class ProfileSetup(StatesGroup):
    waiting_for_name = State()
    waiting_for_age = State()
    waiting_for_city = State()
    waiting_for_height = State()
    waiting_for_weight = State()
