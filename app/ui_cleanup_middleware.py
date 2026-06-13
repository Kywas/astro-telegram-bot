from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, TelegramObject

from app.states import AdminPanel, CompatibilityCheck, DailySetup, MoonDetails, PartnerSetup, PreferencesSetup, ProfileSetup

_DELETE_AFTER_TEXT_STATES = {
    ProfileSetup.waiting_birth_date.state,
    ProfileSetup.waiting_birth_time.state,
    ProfileSetup.waiting_city.state,
    CompatibilityCheck.waiting_partner_birth_date.state,
    CompatibilityCheck.waiting_partner_birth_time.state,
    CompatibilityCheck.waiting_partner_city.state,
    PartnerSetup.waiting_name.state,
    PartnerSetup.waiting_birth_date.state,
    PartnerSetup.waiting_birth_time.state,
    PartnerSetup.waiting_city.state,
    MoonDetails.waiting_day_month.state,
    DailySetup.waiting_custom_time.state,
    AdminPanel.waiting_broadcast_text.state,
    AdminPanel.waiting_grant_input.state,
    PreferencesSetup.waiting_birth_date.state,
    PreferencesSetup.waiting_birth_time.state,
    PreferencesSetup.waiting_current_city.state,
}


class DeleteUserInputMiddleware(BaseMiddleware):
    """Remove user commands and wizard inputs in private chat after handling."""

    async def __call__(self, handler, event: TelegramObject, data: dict):
        state: FSMContext | None = data.get("state")
        state_before = await state.get_state() if state else None
        result = await handler(event, data)
        if not isinstance(event, Message):
            return result

        user = event.from_user
        if user is None or user.is_bot or event.successful_payment is not None:
            return result

        text = (event.text or "").strip()
        should_delete = text.startswith("/") or (
            state_before is not None and state_before in _DELETE_AFTER_TEXT_STATES
        )
        if not should_delete:
            return result

        try:
            await event.delete()
        except TelegramBadRequest:
            pass
        return result
