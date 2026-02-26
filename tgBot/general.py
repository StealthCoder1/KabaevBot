"""Compatibility wrapper for the old import path.

Main app entrypoints were moved into tgBot.bot.app.
"""

from tgBot.bot.app import get_application, start_bot
from tgBot.bot.shared import router

__all__ = ["get_application", "start_bot", "router"]
