from aiogram.fsm.state import State, StatesGroup


class LeadStates(StatesGroup):
    waiting_contact = State()


class AdminStates(StatesGroup):
    waiting_auto_in_path_channel_id = State()
    waiting_leads_channel_id = State()
