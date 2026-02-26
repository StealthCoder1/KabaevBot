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


async def _send_daily_brand_question(bot: Bot) -> None:
    async with async_session() as session:
        result = await session.execute(select(User.telegram_id))
        user_ids = _normalize_user_ids(result.all())

    if not user_ids:
        return

    for user_id in user_ids:
        try:
            await bot.send_message(chat_id=user_id, text=DAILY_BRAND_QUESTION_TEXT)
        except Exception as exc:
            logger.error(f"Не удалось отправить ежедневную рассылку пользователю {user_id}: {exc}")
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

    for admin_id in ADMIN_TG_ID:
        try:
            await bot.send_message(admin_id, "Бот запущен. Команда админки: /admin")
        except Exception as exc:
            logger.info(f"Не удалось написать администратору {admin_id}: {exc}")

    daily_broadcast_task = asyncio.create_task(_daily_brand_question_loop(bot))
    try:
        await dp.start_polling(bot)
    finally:
        daily_broadcast_task.cancel()
        try:
            await daily_broadcast_task
        except asyncio.CancelledError:
            pass
