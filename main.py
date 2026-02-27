import asyncio
import os
import random

from aiogram.exceptions import TelegramNetworkError

from db.ssh_tunnel import start_ssh_tunnel_from_env, stop_ssh_tunnel
from Data.config import DEBUG
from log import logger

BOT_RESTART_BASE_DELAY_SECONDS = float(os.getenv("BOT_RESTART_BASE_DELAY_SECONDS", "2"))
BOT_RESTART_MAX_DELAY_SECONDS = float(os.getenv("BOT_RESTART_MAX_DELAY_SECONDS", "60"))


def _get_restart_delay(attempt: int) -> float:
    exp = max(0, min(attempt - 1, 8))
    base_delay = BOT_RESTART_BASE_DELAY_SECONDS * (2**exp)
    bounded_delay = min(base_delay, BOT_RESTART_MAX_DELAY_SECONDS)
    return bounded_delay + random.uniform(0.0, 1.0)


async def _run_bot_forever() -> None:
    from db.connect import create_all_tables
    from tgBot.general import start_bot

    attempt = 0
    while True:
        try:
            start_ssh_tunnel_from_env(force=DEBUG)
            await create_all_tables()
            await start_bot()
            attempt = 0
            logger.warning("Polling stopped without exception. Restarting in 1 second.")
            await asyncio.sleep(1)
        except (asyncio.CancelledError, KeyboardInterrupt):
            raise
        except TelegramNetworkError:
            attempt += 1
            delay = _get_restart_delay(attempt)
            logger.exception(
                "Bot stopped because of Telegram network error. Restarting in %.1f seconds.",
                delay,
            )
            await asyncio.sleep(delay)
        except Exception:
            attempt += 1
            delay = _get_restart_delay(attempt)
            logger.exception(
                "Bot crashed unexpectedly. Restarting in %.1f seconds.",
                delay,
            )
            await asyncio.sleep(delay)


async def main():
    try:
        await _run_bot_forever()
    except KeyboardInterrupt:
        logger.info("Shutdown requested by keyboard interrupt.")
        raise
    finally:
        stop_ssh_tunnel()


if __name__ == '__main__':
    print('[+]Start bot[+]')
    asyncio.run(main())
