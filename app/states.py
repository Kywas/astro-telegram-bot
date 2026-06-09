from aiogram.fsm.state import State, StatesGroup


class ProfileSetup(StatesGroup):
    waiting_birth_date = State()
    waiting_birth_time = State()
    waiting_city = State()
    waiting_relationship = State()
    waiting_goal = State()


class CompatibilityCheck(StatesGroup):
    waiting_partner_birth_date = State()
    waiting_partner_birth_time = State()
    waiting_partner_city = State()


class PartnerSetup(StatesGroup):
    waiting_name = State()
    waiting_birth_date = State()
    waiting_birth_time = State()
    waiting_city = State()


class MoonDetails(StatesGroup):
    waiting_day_month = State()


class PreferencesSetup(StatesGroup):
    waiting_gender = State()
    waiting_relationship = State()
    waiting_goal = State()


class AdminPanel(StatesGroup):
    waiting_broadcast_text = State()
    waiting_broadcast_confirm = State()
    waiting_grant_input = State()


class DailySetup(StatesGroup):
    waiting_custom_time = State()
