from aiogram import BaseMiddleware
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, TelegramObject

from app.states import AdminPanel, CompatibilityCheck, DailySetup, MoonDetails, PartnerSetup, ProfileSetup

_DELETE_AFTER_TEXT_STATES = {
    ProfileSetup.waiting_birth_date.state,
    ProfileSetup.waiting_birth_time.state,
    ProfileSetup.waiting_city.state,
    CompatibilityCheck.waiting_partner_birth_date.state,
    PartnerSetup.waiting_name.state,
    PartnerSetup.waiting_birth_date.state,
    PartnerSetup.waiting_birth_time.state,
    PartnerSetup.waiting_city.state,
    MoonDetails.waiting_day_month.state,
    DailySetup.waiting_custom_time.state,
    AdminPanel.waiting_broadcast_text.state,
    AdminPanel.waiting_grant_input.state,
}


class DeleteUserInputMiddleware(BaseMiddleware):
    """Remove user commands and wizard inputs in private chat after handling."""

    async def __call__(self, handler, event: TelegramObject, data: dict):
        result = await handler(event, data)
        if not isinstance(event, Message):
            return result

        user = event.from_user
        if user is None or user.is_bot or event.successful_payment is not None:
            return result

        text = (event.text or "").strip()
        state: FSMContext | None = data.get("state")
        current_state = await state.get_state() if state else None
        should_delete = text.startswith("/") or (
            current_state is not None and current_state in _DELETE_AFTER_TEXT_STATES
        )
        if not should_delete:
            return result

        try:
            await event.delete()
        except TelegramBadRequest:
            pass
        return result
