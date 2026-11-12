from collections.abc import Awaitable, Callable
from typing import Any

from aiogram.dispatcher.middlewares.base import BaseMiddleware
from aiogram.types import CallbackQuery, Message, TelegramObject


class OwnerOnly(BaseMiddleware):
    def __init__(self, owner_id: int) -> None:
        self.owner_id = owner_id

    async def __call__(
        self,
        handler: Callable[[TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        # Foreign users and groups get no reply and no callback answer.
        if not _is_owner_in_private(event, self.owner_id):
            return None
        return await handler(event, data)


def _is_owner_in_private(event: TelegramObject, owner_id: int) -> bool:
    if isinstance(event, CallbackQuery):
        chat = None if event.message is None else event.message.chat
        user = event.from_user
    elif isinstance(event, Message):
        chat = event.chat
        user = event.from_user
    else:
        return False
    return user is not None and user.id == owner_id and chat is not None and chat.type == "private"
