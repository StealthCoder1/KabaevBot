import os

from aiogram.utils.backoff import BackoffConfig

from tgBot.bot.shared import *

# Import handler modules for side effects (router registration)
from tgBot.bot.handlers import start_admin as _start_admin_handlers  # noqa: F401
from tgBot.bot.handlers import auto as _auto_handlers  # noqa: F401
from tgBot.bot.handlers import moto as _moto_handlers  # noqa: F401
from tgBot.bot.handlers import info as _info_handlers  # noqa: F401
from tgBot.bot.handlers import contact as _contact_handlers  # noqa: F401
from tgBot.bot.handlers import channel as _channel_handlers  # noqa: F401

DAILY_BRAND_QUESTION_TEXT = "Какая марка авто наиболее интересна?"
DAILY_BRAND_QUESTION_INTERVAL_SECONDS = 24 * 60 * 60
# Keep long polling below common 30-second proxy/load-balancer idle limits.
POLLING_TIMEOUT_SECONDS = int(os.getenv("POLLING_TIMEOUT_SECONDS", "25"))
POLLING_BACKOFF_CONFIG = BackoffConfig(
    min_delay=float(os.getenv("POLLING_RETRY_MIN_DELAY_SECONDS", "1")),
    max_delay=float(os.getenv("POLLING_RETRY_MAX_DELAY_SECONDS", "30")),
    factor=float(os.getenv("POLLING_RETRY_FACTOR", "1.5")),
    jitter=float(os.getenv("POLLING_RETRY_JITTER", "0.2")),
)


async def _send_daily_brand_question(bot: Bot) -> None:
    user_ids = await get_known_user_ids(exclude_user_ids={bot.id})
    if not user_ids:
        return

    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=DAILY_BRAND_QUESTION_TEXT)
        except Exception as exc:
            await handle_user_delivery_error(user_id, exc, action="отправить ежедневную рассылку")
        await asyncio.sleep(0.05)


async def _daily_brand_question_loop(bot: Bot) -> None:
    while True:
        await asyncio.sleep(DAILY_BRAND_QUESTION_INTERVAL_SECONDS)
        try:
            await _send_daily_brand_question(bot)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            logger.error(f"Ошибка фоновой ежедневной рассылки: {exc}")


def get_application():
    dp = Dispatcher()
    dp.include_router(router)
    return dp


async def start_bot():
    logger.info("Бот запущен")
    bot = Bot(token=TG_BOT_TOKEN)
    dp = get_application()

    try:
        await sync_admin_users_from_config()
    except Exception as exc:
        logger.error(f"Не удалось синхронизировать admin_users: {exc}")

    try:
        await ensure_channels_config_defaults()
    except Exception as exc:
        logger.error(f"Failed to create default channels config: {exc}")

    for admin_id in get_configured_admin_ids(exclude_user_ids={bot.id}):
        try:
            await bot.send_message(admin_id, "Бот запущен. Команда админки: /admin")
        except Exception as exc:
            log_admin_delivery_error(admin_id, exc, action="написать")

    daily_broadcast_task = asyncio.create_task(_daily_brand_question_loop(bot))
    try:
        await dp.start_polling(
            bot,
            polling_timeout=POLLING_TIMEOUT_SECONDS,
            backoff_config=POLLING_BACKOFF_CONFIG,
            allowed_updates=dp.resolve_used_update_types(),
            handle_signals=False,
            close_bot_session=True,
        )
    finally:
        daily_broadcast_task.cancel()
        try:
            await daily_broadcast_task
        except asyncio.CancelledError:
            pass
