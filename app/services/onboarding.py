"""Profile onboarding wizard helpers."""
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

from app.bot_context import db
from app.i18n import t
from app.keyboards import home_goal_keyboard, onboarding_relationship_keyboard
from app.states import ProfileSetup
from app.ui import edit_or_send, show_panel_from_message

async def show_relationship_onboarding_panel(
    locale: str,
    *,
    message: Message | None = None,
    callback: CallbackQuery | None = None,
) -> None:
    text = t(locale, "choose_relationship_onboarding")
    keyboard = onboarding_relationship_keyboard(locale)
    if callback is not None:
        await edit_or_send(callback, text, inline_keyboard=keyboard)
    elif message is not None:
        await show_panel_from_message(message, text, reply_markup=keyboard)


async def show_goal_onboarding_panel(
    locale: str,
    *,
    message: Message | None = None,
    callback: CallbackQuery | None = None,
) -> None:
    text = t(locale, "choose_goal_onboarding")
    keyboard = home_goal_keyboard(locale, back_callback=None)
    if callback is not None:
        await edit_or_send(callback, text, inline_keyboard=keyboard)
    elif message is not None:
        await show_panel_from_message(message, text, reply_markup=keyboard)


async def onboarding_step_needed(user_id: int) -> str | None:
    profile = await db.get_user(user_id)
    if not profile or not profile.sign:
        return None
    if not profile.relationship_status:
        return "relationship"
    if not profile.goal:
        return "goal"
    return None


async def resume_onboarding_if_needed(
    user_id: int,
    locale: str,
    state: FSMContext,
    *,
    message: Message | None = None,
    callback: CallbackQuery | None = None,
) -> bool:
    step = await onboarding_step_needed(user_id)
    if step == "relationship":
        await state.set_state(ProfileSetup.waiting_relationship)
        await show_relationship_onboarding_panel(locale, message=message, callback=callback)
        return True
    if step == "goal":
        await state.set_state(ProfileSetup.waiting_goal)
        await show_goal_onboarding_panel(locale, message=message, callback=callback)
        return True
    return False


