from __future__ import annotations

from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import BaseMiddleware, Bot, types

from Data.config import (
    REQUIRE_CHANNEL_SUBSCRIPTION,
    REQUIRED_CHANNEL_CHAT_ID,
    REQUIRED_CHANNEL_URL,
    REQUIRED_CHANNEL_USERNAME,
)
from log import logger
from tgBot.bot.shared import HOME_MENU_TEXT, get_start_keyboard, is_admin
from tgBot.keyboards import (
    SUBSCRIPTION_CHECK_CALLBACK_DATA,
    get_required_subscription_keyboard,
)


class RequiredChannelSubscriptionMiddleware(BaseMiddleware):
    SUBSCRIPTION_REQUIRED_TEXT = "Чтобы пользоваться ботом, подпишитесь на наш Telegram-канал."

    async def __call__(
        self,
        handler: Callable[[types.TelegramObject, dict[str, Any]], Awaitable[Any]],
        event: types.TelegramObject,
        data: dict[str, Any],
    ) -> Any:
        if not REQUIRE_CHANNEL_SUBSCRIPTION:
            return await handler(event, data)

        user = self._extract_user(event)
        if user is None or user.is_bot or is_admin(user.id):
            return await handler(event, data)

        if not self._is_private_dialog_event(event):
            return await handler(event, data)

        bot = data.get("bot")
        if not isinstance(bot, Bot):
            return await handler(event, data)

        if isinstance(event, types.CallbackQuery) and event.data == SUBSCRIPTION_CHECK_CALLBACK_DATA:
            await self._handle_subscription_check_callback(event, data, bot=bot)
            return None

        if await self._is_user_subscribed(bot=bot, user_id=user.id):
            return await handler(event, data)

        await self._send_subscription_required_prompt(event, bot=bot)
        return None

    @staticmethod
    def _extract_user(event: types.TelegramObject) -> types.User | None:
        if isinstance(event, types.Message):
            return event.from_user
        if isinstance(event, types.CallbackQuery):
            return event.from_user
        return None

    @staticmethod
    def _is_private_dialog_event(event: types.TelegramObject) -> bool:
        if isinstance(event, types.Message):
            return bool(event.chat and event.chat.type == "private")
        if isinstance(event, types.CallbackQuery):
            message = event.message
            return bool(message and getattr(message, "chat", None) and message.chat.type == "private")
        return False

    @staticmethod
    def _required_channel_target() -> int | str | None:
        if REQUIRED_CHANNEL_CHAT_ID is not None:
            return REQUIRED_CHANNEL_CHAT_ID
        if REQUIRED_CHANNEL_USERNAME:
            return f"@{REQUIRED_CHANNEL_USERNAME.lstrip('@')}"
        return None

    async def _is_user_subscribed(self, *, bot: Bot, user_id: int) -> bool:
        chat_target = self._required_channel_target()
        if chat_target is None:
            logger.warning(
                "Channel subscription check is enabled, but REQUIRED_CHANNEL_CHAT_ID/REQUIRED_CHANNEL_USERNAME is not configured."
            )
            return True

        try:
            member = await bot.get_chat_member(chat_id=chat_target, user_id=user_id)
            status = getattr(member, "status", None)
            status_value = getattr(status, "value", str(status)).lower()
            return status_value in {"creator", "owner", "administrator", "member", "restricted"}
        except Exception as exc:
            logger.warning(
                f"Failed to check channel subscription for user_id={user_id}, chat_target={chat_target}: {exc}"
            )
            return False

    async def _send_subscription_required_prompt(
        self,
        event: types.TelegramObject,
        *,
        bot: Bot,
    ) -> None:
        markup = get_required_subscription_keyboard(channel_url=REQUIRED_CHANNEL_URL)
        if isinstance(event, types.Message):
            await event.answer(self.SUBSCRIPTION_REQUIRED_TEXT, reply_markup=markup)
            return

        if isinstance(event, types.CallbackQuery):
            await event.answer("Сначала подпишитесь на канал.")
            await bot.send_message(
                chat_id=event.from_user.id,
                text=self.SUBSCRIPTION_REQUIRED_TEXT,
                reply_markup=markup,
            )

    async def _handle_subscription_check_callback(
        self,
        callback: types.CallbackQuery,
        data: dict[str, Any],
        *,
        bot: Bot,
    ) -> None:
        if await self._is_user_subscribed(bot=bot, user_id=callback.from_user.id):
            state = data.get("state")
            if state is not None:
                await state.clear()

            await callback.answer("Подписка подтверждена.")
            await bot.send_message(
                chat_id=callback.from_user.id,
                text=HOME_MENU_TEXT,
                reply_markup=get_start_keyboard(),
                parse_mode="HTML",
            )
            return

        await self._send_subscription_required_prompt(callback, bot=bot)
