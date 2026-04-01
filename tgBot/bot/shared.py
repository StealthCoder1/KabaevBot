import asyncio
import os
import random
import re
from collections import defaultdict
from datetime import datetime, timedelta, timezone
from pathlib import Path
from types import SimpleNamespace

from aiogram import Bot, Dispatcher, Router, F, types
from aiogram.exceptions import TelegramAPIError, TelegramBadRequest, TelegramForbiddenError, TelegramNotFound
from aiogram.filters import Command, CommandStart
from aiogram.fsm.context import FSMContext
from sqlalchemy import delete, select
from sqlalchemy.exc import IntegrityError

from Data.config import TG_BOT_TOKEN, ADMIN_TG_ID
from db.connect import async_session
from db import models as db_models
from log import logger
from tgBot.catalogs import (
    _auto_category_has_countries,
    _get_auto_category_label,
    _get_auto_country_title,
    _get_auto_model_description_text,
    _get_auto_model_country_id,
    _get_auto_model_lead_message,
    _get_auto_model_placeholder_text,
    _get_auto_model_photo_path,
    _get_auto_model_title,
    _get_max_profit_lots,
    _get_moto_class_config,
    _get_moto_intro_texts,
    _get_moto_model_description_text,
    _get_moto_model_lead_message,
    _get_moto_model_placeholder_text,
    _get_moto_model_title,
    _get_moto_models_keyboard,
    _join_catalog_lines,
)
from tgBot.keyboards import (
    get_admin_keyboard,
    get_auto_countries_keyboard,
    get_auto_country_models_keyboard,
    get_auto_in_path_post_keyboard,
    get_auto_model_actions_keyboard,
    get_best_deals_keyboard,
    get_contact_request_keyboard,
    get_electric_models_keyboard,
    get_guarantees_keyboard,
    get_guarantees_risks_keyboard,
    get_max_profit_keyboard,
    get_moto_classes_keyboard,
    get_moto_model_actions_keyboard,
    get_post_actions_keyboard,
    get_price_range_keyboard,
    get_quick_main_auction_keyboard,
    get_quick_main_credit_keyboard,
    get_quick_main_delivery_keyboard,
    get_quick_main_keyboard,
    get_start_keyboard,
    get_user_reply_keyboard,
)
from tgBot.states import LeadStates
from tgBot.texts import (
    BACK_BUTTON_TEXT,
    BEST_DEALS_NEXT_STEP_TEXT,
    BUDGET_PROMPT_TEXT,
    CONTACT_MANAGER_TEXT,
    HOME_MENU_TEXT,
    HOME_REPLY_BUTTON_TEXT,
    LEAD_CONTACT_REQUEST_TEXT,
    LEAD_SAVED_TEXT,
    MAIN_MENU_ACTION_TEXT,
    MAIN_MENU_VARIANT_TEXT,
    MOTO_HINT_FALLBACK_TEXT,
    MOTO_INTRO_FALLBACK_TEXT,
    MOTO_MODEL_RESOLVE_ERROR_TEXT,
)

User = db_models.User
Lead = getattr(db_models, "Lead", None)
Channel = getattr(db_models, "Channel", None)
AutoInTransitPost = getattr(db_models, "AutoInTransitPost", None)
AdminUser = getattr(db_models, "AdminUser", None)

router = Router()
media_groups_buffer = defaultdict(list)
media_cache = {}

BROADCAST_SOURCE_CHANNEL_CODE = "broadcast_source"
DEFAULT_BROADCAST_SOURCE_CHANNEL_ID = -1003426962243
DEFAULT_BROADCAST_SOURCE_CHANNEL_TITLE = "Основной канал"
AUTO_IN_PATH_CHANNEL_CODE = "auto_in_path_source"
DEFAULT_AUTO_IN_PATH_CHANNEL_ID = -1003706573371
DEFAULT_AUTO_IN_PATH_CHANNEL_TITLE = "Авто в пути"
LEADS_CHANNEL_CODE = "leads_target"
DEFAULT_LEADS_CHANNEL_TITLE = "Лиды"
POST_LIKE_PROMPT_TEXT = "Если пост понравился, нажмите кнопку ниже."
AUTO_IN_PATH_BROWSER_PROMPT_TEXT = "Выберите, что сделать с этим вариантом."
AUTO_IN_PATH_STICKER_ENV_NAME = "AUTO_IN_PATH_STICKER_ID"
PERMANENT_USER_DELIVERY_ERROR_PATTERNS = (
    "chat not found",
    "user not found",
    "bot was blocked by the user",
    "bot can't initiate conversation with a user",
    "user is deactivated",
    "bots can't send messages to bots",
)


def _pick_max_profit_lot(exclude_id: str | None = None) -> dict[str, str]:
    all_lots = list(_get_max_profit_lots())
    if not all_lots:
        return {
            "id": "max_profit_fallback",
            "title": "Топ выгоды",
            "photo_path": "",
            "text": "Список выгодных лотов временно недоступен. Попробуйте позже.",
        }
    lots = [lot for lot in all_lots if lot.get("id") != exclude_id]
    return random.choice(lots or all_lots)


async def _send_random_max_profit_lot(
    callback: types.CallbackQuery,
    state: FSMContext,
    *,
    exclude_current: bool = False,
) -> None:
    data = await state.get_data()
    current_id = data.get("max_profit_lot_id") if exclude_current else None
    lot = _pick_max_profit_lot(current_id)
    await state.update_data(
        max_profit_lot_id=lot["id"],
        max_profit_lot_title=lot["title"],
    )
    reply_markup = get_max_profit_keyboard()
    photo_path = lot.get("photo_path")
    if photo_path:
        path_obj = Path(photo_path)
        if not path_obj.is_absolute():
            path_obj = Path(__file__).resolve().parents[2] / path_obj
        if path_obj.exists():
            try:
                await callback.message.answer_photo(
                    photo=types.FSInputFile(path_obj),
                    caption=lot["text"],
                    reply_markup=reply_markup,
                )
                return
            except Exception as exc:
                logger.error(f"Не удалось отправить фото max_profit лота {lot['id']}: {exc}")

    await callback.message.answer(lot["text"], reply_markup=reply_markup)


async def _show_auto_model_card(
    callback: types.CallbackQuery,
    *,
    category_id: str,
    model_id: str,
    country_id: str | None = None,
    back_callback_data: str | None = None,
    source_token: str = "",
) -> None:
    text = _get_auto_model_description_text(category_id, model_id, country_id=country_id)
    reply_markup = get_auto_model_actions_keyboard(
        category_id,
        model_id,
        country_id=country_id,
        back_callback_data=back_callback_data,
        source_token=source_token,
    )
    photo_path = _get_auto_model_photo_path(category_id, model_id, country_id=country_id)
    if photo_path:
        path_obj = Path(photo_path)
        if not path_obj.is_absolute():
            # shared.py lives in tgBot/bot/, so project root is two levels above tgBot
            path_obj = Path(__file__).resolve().parents[2] / path_obj
        if path_obj.exists():
            try:
                await callback.message.answer_photo(
                    photo=types.FSInputFile(path_obj),
                    caption=text,
                    reply_markup=reply_markup,
                )
                return
            except Exception as exc:
                logger.error(
                    f"Не удалось отправить фото карточки авто {category_id}/{country_id or '-'}"
                    f"/{model_id}: {exc}"
                )

    await callback.message.answer(text, reply_markup=reply_markup)


async def _show_moto_model_card(
    callback: types.CallbackQuery,
    *,
    class_id: str,
    model_id: str,
) -> None:
    text = _get_moto_model_description_text(class_id, model_id)
    await callback.message.answer(
        text,
        reply_markup=get_moto_model_actions_keyboard(class_id, model_id),
    )


def _extract_model_id(callback_data: str) -> str:
    return callback_data.rsplit(":", maxsplit=1)[-1]


def _model_column_names(model_cls) -> set[str]:
    try:
        return {column.name for column in model_cls.__table__.columns}
    except Exception:
        return set()


def _filter_model_kwargs(model_cls, **kwargs):
    if model_cls is None:
        return {}
    columns = _model_column_names(model_cls)
    return {key: value for key, value in kwargs.items() if key in columns}


def _lead_stub(
    *,
    from_user: types.User,
    action: str,
    phone: str | None = None,
    customer_name: str | None = None,
    price_range: str | None = None,
    message_text: str | None = None,
):
    return SimpleNamespace(
        id=None,
        action=action,
        user_telegram_id=from_user.id,
        username=from_user.username,
        customer_name=customer_name,
        phone=phone,
        price_range=price_range,
        message_text=message_text,
        created_at=datetime.utcnow(),
    )


def _normalize_user_ids(rows) -> list[int]:
    user_ids: list[int] = []
    for row in rows:
        value = row[0]
        try:
            user_ids.append(int(value))
        except (TypeError, ValueError):
            logger.warning(f"Пропущен некорректный telegram_id в users: {value!r}")
    return user_ids


def _deduplicate_user_ids(user_ids: list[int]) -> list[int]:
    unique_user_ids: list[int] = []
    seen_user_ids: set[int] = set()
    for user_id in user_ids:
        if user_id in seen_user_ids:
            continue
        seen_user_ids.add(user_id)
        unique_user_ids.append(user_id)
    return unique_user_ids


def _telegram_error_text(exc: Exception) -> str:
    return str(exc).lower().strip()


def _is_permanent_user_delivery_error(exc: Exception) -> bool:
    error_text = _telegram_error_text(exc)
    if any(pattern in error_text for pattern in PERMANENT_USER_DELIVERY_ERROR_PATTERNS):
        return True
    if isinstance(exc, TelegramNotFound):
        return True
    if isinstance(exc, TelegramBadRequest):
        return "chat not found" in error_text or "user not found" in error_text
    if isinstance(exc, TelegramForbiddenError):
        return True
    return isinstance(exc, TelegramAPIError) and "bots can't send messages to bots" in error_text


async def get_known_user_ids(*, exclude_user_ids: set[int] | None = None) -> list[int]:
    async with async_session() as session:
        result = await session.execute(select(User.telegram_id))
        user_ids = _normalize_user_ids(result.all())

    unique_user_ids = _deduplicate_user_ids(user_ids)
    if not exclude_user_ids:
        return unique_user_ids
    return [user_id for user_id in unique_user_ids if user_id not in exclude_user_ids]


def get_configured_admin_ids(*, exclude_user_ids: set[int] | None = None) -> list[int]:
    unique_admin_ids = _deduplicate_user_ids(list(ADMIN_TG_ID))
    if not exclude_user_ids:
        return unique_admin_ids
    return [admin_id for admin_id in unique_admin_ids if admin_id not in exclude_user_ids]


def _user_tg_id_db_value(telegram_id: int):
    try:
        column = User.__table__.columns["telegram_id"]
        python_type = getattr(column.type, "python_type", None)
        if python_type is str:
            return str(telegram_id)
    except Exception:
        pass
    return telegram_id


def get_admin_role(user_id: int) -> str | None:
    if not ADMIN_TG_ID:
        return None
    if user_id == ADMIN_TG_ID[0]:
        return "owner"
    if user_id in ADMIN_TG_ID[1:]:
        return "admin"
    return None


def is_admin(user_id: int) -> bool:
    return get_admin_role(user_id) is not None


async def ensure_user_exists(from_user: types.User) -> None:
    if getattr(from_user, "is_bot", False):
        return

    db_telegram_id = _user_tg_id_db_value(from_user.id)
    user_role = get_admin_role(from_user.id) or "user"
    first_name = getattr(from_user, "first_name", None)
    last_name = getattr(from_user, "last_name", None)
    async with async_session() as session:
        result = await session.execute(select(User).where(User.telegram_id == db_telegram_id))
        user = result.scalar_one_or_none()
        if user is not None:
            updated = False
            if getattr(user, "role", None) != user_role:
                user.role = user_role
                updated = True
            if getattr(user, "username", None) != from_user.username:
                user.username = from_user.username
                updated = True
            if hasattr(user, "first_name") and getattr(user, "first_name", None) != first_name:
                user.first_name = first_name
                updated = True
            if hasattr(user, "last_name") and getattr(user, "last_name", None) != last_name:
                user.last_name = last_name
                updated = True
            if updated:
                await session.commit()
            return

        session.add(
            User(
                role=user_role,
                telegram_id=db_telegram_id,
                username=from_user.username,
                first_name=first_name,
                last_name=last_name,
            )
        )
        await session.commit()


async def delete_user_by_telegram_id(telegram_id: int) -> int:
    db_telegram_id = _user_tg_id_db_value(telegram_id)
    async with async_session() as session:
        result = await session.execute(delete(User).where(User.telegram_id == db_telegram_id))
        await session.commit()
        return int(result.rowcount or 0)


async def handle_user_delivery_error(user_id: int, exc: Exception, *, action: str) -> bool:
    if _is_permanent_user_delivery_error(exc):
        removed = await delete_user_by_telegram_id(user_id)
        logger.warning(
            f"Не удалось {action} пользователю {user_id}: {exc}. Пользователь удалён из БД: removed={removed}"
        )
        return True

    logger.error(f"Не удалось {action} пользователю {user_id}: {exc}")
    return False


def log_admin_delivery_error(admin_id: int, exc: Exception, *, action: str) -> None:
    log_method = logger.warning if _is_permanent_user_delivery_error(exc) else logger.error
    log_method(f"Не удалось {action} администратору {admin_id}: {exc}")


async def sync_admin_users_from_config() -> None:
    if not ADMIN_TG_ID:
        return
    if AdminUser is None:
        logger.debug("Модель AdminUser отсутствует в db.models, sync_admin_users пропущен")
        return

    desired_roles = {admin_id: get_admin_role(admin_id) or "admin" for admin_id in ADMIN_TG_ID}

    async with async_session() as session:
        result = await session.execute(select(AdminUser))
        existing_by_tg_id = {row.telegram_id: row for row in result.scalars().all()}
        admin_columns = _model_column_names(AdminUser)

        for admin_id, role in desired_roles.items():
            admin = existing_by_tg_id.get(admin_id)
            if admin is None:
                session.add(
                    AdminUser(
                        **_filter_model_kwargs(
                            AdminUser,
                            telegram_id=admin_id,
                            role=role,
                            is_active=True,
                        )
                    )
                )
                continue

            if "role" in admin_columns:
                admin.role = role
            if "is_active" in admin_columns:
                admin.is_active = True

        for tg_id, admin in existing_by_tg_id.items():
            if tg_id not in desired_roles and "is_active" in admin_columns:
                admin.is_active = False

        await session.commit()


async def ensure_channels_config_defaults() -> None:
    if Channel is None:
        logger.info("Модель Channel отсутствует в db.models, сидинг channels пропущен")
        return

    default_channels: list[dict[str, int | str]] = [
        {
            "code": BROADCAST_SOURCE_CHANNEL_CODE,
            "chat_id": DEFAULT_BROADCAST_SOURCE_CHANNEL_ID,
            "title": DEFAULT_BROADCAST_SOURCE_CHANNEL_TITLE,
        },
        {
            "code": AUTO_IN_PATH_CHANNEL_CODE,
            "chat_id": DEFAULT_AUTO_IN_PATH_CHANNEL_ID,
            "title": DEFAULT_AUTO_IN_PATH_CHANNEL_TITLE,
        },
    ]

    now = datetime.utcnow()
    async with async_session() as session:
        result = await session.execute(select(Channel.code))
        existing_codes = {row[0] for row in result.all()}
        created_any = False
        for channel_cfg in default_channels:
            if channel_cfg["code"] in existing_codes:
                continue
            session.add(
                Channel(
                    **_filter_model_kwargs(
                        Channel,
                        code=channel_cfg["code"],
                        chat_id=channel_cfg["chat_id"],
                        title=channel_cfg["title"],
                        created_at=now,
                        updated_at=now,
                    )
                )
            )
            created_any = True

        if created_any:
            await session.commit()


async def get_channel_chat_id(code: str, fallback: int | None = None) -> int | None:
    if Channel is None:
        return fallback

    async with async_session() as session:
        result = await session.execute(select(Channel.chat_id).where(Channel.code == code))
        value = result.scalar_one_or_none()
        if value is None:
            return fallback
        try:
            return int(value)
        except (TypeError, ValueError):
            logger.warning(f"Некорректный chat_id в channels для code={code}: {value!r}")
            return fallback


async def get_channel_record(code: str):
    if Channel is None:
        return None

    async with async_session() as session:
        result = await session.execute(select(Channel).where(Channel.code == code))
        return result.scalar_one_or_none()


async def set_channel_chat_id(code: str, chat_id: int, title: str | None = None) -> None:
    if Channel is None:
        logger.info("Модель Channel отсутствует в db.models, обновление channels пропущено")
        return

    now = datetime.utcnow()
    async with async_session() as session:
        result = await session.execute(select(Channel).where(Channel.code == code))
        record = result.scalar_one_or_none()
        if record is None:
            session.add(
                Channel(
                    **_filter_model_kwargs(
                        Channel,
                        code=code,
                        chat_id=chat_id,
                        title=title,
                        created_at=now,
                        updated_at=now,
                    )
                )
            )
        else:
            record.chat_id = chat_id
            if title is not None and hasattr(record, "title"):
                record.title = title
            if hasattr(record, "updated_at"):
                record.updated_at = now
        await session.commit()


async def get_auto_in_path_channel_id() -> int | None:
    return await get_channel_chat_id(AUTO_IN_PATH_CHANNEL_CODE)


async def set_auto_in_path_channel_id(chat_id: int, title: str | None = None) -> None:
    await set_channel_chat_id(AUTO_IN_PATH_CHANNEL_CODE, chat_id, title=title)


async def get_broadcast_source_channel_id() -> int | None:
    return await get_channel_chat_id(BROADCAST_SOURCE_CHANNEL_CODE)


async def set_broadcast_source_channel_id(chat_id: int, title: str | None = None) -> None:
    await set_channel_chat_id(BROADCAST_SOURCE_CHANNEL_CODE, chat_id, title=title)


async def get_leads_channel_id() -> int | None:
    return await get_channel_chat_id(LEADS_CHANNEL_CODE)


async def set_leads_channel_id(chat_id: int, title: str | None = None) -> None:
    await set_channel_chat_id(LEADS_CHANNEL_CODE, chat_id, title=title)


async def save_lead(
    from_user: types.User,
    action: str,
    phone: str | None = None,
    customer_name: str | None = None,
    price_range: str | None = None,
    message_text: str | None = None,
) -> Lead:
    if Lead is None:
        logger.info("Модель Lead отсутствует в db.models, лид не сохраняется в БД")
        return _lead_stub(
            from_user=from_user,
            action=action,
            phone=phone,
            customer_name=customer_name,
            price_range=price_range,
            message_text=message_text,
        )

    async with async_session() as session:
        lead = Lead(
            **_filter_model_kwargs(
                Lead,
                user_telegram_id=from_user.id,
                username=from_user.username,
                full_name=from_user.full_name,
                action=action,
                phone=phone,
                customer_name=customer_name,
                price_range=price_range,
                message_text=message_text,
            )
        )
        session.add(lead)
        await session.commit()
        await session.refresh(lead)
        return lead


async def save_auto_in_transit_post(message: types.Message) -> None:
    if AutoInTransitPost is None:
        return

    source_channel_id = await get_auto_in_path_channel_id()
    if source_channel_id is None or message.chat.id != source_channel_id:
        return

    posted_at = message.date.replace(tzinfo=None) if message.date else None
    record = AutoInTransitPost(
        channel_id=message.chat.id,
        message_id=message.message_id,
        media_group_id=message.media_group_id,
        posted_at=posted_at,
    )

    async with async_session() as session:
        session.add(record)
        try:
            await session.commit()
        except IntegrityError:
            await session.rollback()


async def get_auto_in_transit_copy_batches(*, newest_first: bool = False) -> list[list[int]]:
    if AutoInTransitPost is None:
        return []

    source_channel_id = await get_auto_in_path_channel_id()
    if source_channel_id is None:
        return []

    async with async_session() as session:
        result = await session.execute(
            select(AutoInTransitPost)
            .where(AutoInTransitPost.channel_id == source_channel_id)
            .order_by(AutoInTransitPost.posted_at.asc(), AutoInTransitPost.message_id.asc())
        )
        posts = result.scalars().all()

    batches: list[list[int]] = []
    i = 0
    while i < len(posts):
        current = posts[i]
        if current.media_group_id:
            group_id = current.media_group_id
            group_message_ids: list[int] = []
            while i < len(posts) and posts[i].media_group_id == group_id:
                group_message_ids.append(posts[i].message_id)
                i += 1
            batches.extend(_chunk_message_ids(group_message_ids, 100))
            continue

        batches.append([current.message_id])
        i += 1

    if newest_first:
        batches.reverse()

    return batches


def _chunk_message_ids(message_ids: list[int], size: int) -> list[list[int]]:
    return [message_ids[i : i + size] for i in range(0, len(message_ids), size)]


def _copied_message_id(value) -> int | None:
    if value is None:
        return None

    if isinstance(value, int):
        return value

    if isinstance(value, dict):
        raw_message_id = value.get("message_id")
    else:
        raw_message_id = getattr(value, "message_id", None)

    if raw_message_id is None:
        if isinstance(value, str) and value.isdigit():
            return int(value)
        return None

    try:
        return int(raw_message_id)
    except (TypeError, ValueError):
        return None


async def _attach_post_actions_keyboard_to_message(
    bot: Bot,
    user_id: int,
    copied_message,
    source_chat_id: int,
    source_message_id: int,
    *,
    log_failures: bool = True,
) -> bool:
    copied_id = _copied_message_id(copied_message)
    if copied_id is None:
        return False

    last_exc: Exception | None = None
    for delay in (0.0, 0.15, 0.35, 0.7):
        if delay:
            await asyncio.sleep(delay)
        try:
            await bot.edit_message_reply_markup(
                chat_id=user_id,
                message_id=copied_id,
                reply_markup=get_post_actions_keyboard(source_chat_id, source_message_id),
            )
            return True
        except Exception as exc:
            last_exc = exc

    if log_failures:
        logger.warning(
            f"Не удалось добавить кнопку к посту авто в пути пользователю {user_id}, "
            f"message_id={copied_id}: {last_exc}"
        )
    return False


async def _send_post_actions_prompt(
    bot: Bot,
    user_id: int,
    source_chat_id: int,
    source_message_id: int,
    *,
    reply_to_message_id: int | None = None,
) -> None:
    try:
        await bot.send_message(
            chat_id=user_id,
            text=POST_LIKE_PROMPT_TEXT,
            reply_markup=get_post_actions_keyboard(source_chat_id, source_message_id),
            reply_to_message_id=reply_to_message_id,
            allow_sending_without_reply=True,
        )
    except Exception as exc:
        logger.warning(
            f"Не удалось отправить кнопку для поста авто в пути пользователю {user_id}, "
            f"source_message_id={source_message_id}: {exc}"
        )


async def _send_optional_auto_in_path_sticker(bot: Bot, user_id: int) -> None:
    sticker_id = os.getenv(AUTO_IN_PATH_STICKER_ENV_NAME, "").strip()
    if not sticker_id:
        return

    try:
        await bot.send_sticker(chat_id=user_id, sticker=sticker_id)
    except Exception as exc:
        logger.warning(f"Не удалось отправить стикер авто в пути пользователю {user_id}: {exc}")


async def _send_auto_in_path_actions_prompt(
    bot: Bot,
    user_id: int,
    source_chat_id: int,
    source_message_id: int,
    *,
    next_post_index: int | None,
    reply_to_message_id: int | None = None,
) -> None:
    last_exc: Exception | None = None
    reply_targets = [reply_to_message_id] if reply_to_message_id is not None else []
    reply_targets.append(None)
    for current_reply_to in reply_targets:
        try:
            await bot.send_message(
                chat_id=user_id,
                text=AUTO_IN_PATH_BROWSER_PROMPT_TEXT,
                reply_markup=get_auto_in_path_post_keyboard(
                    source_chat_id,
                    source_message_id,
                    next_post_index=next_post_index,
                ),
                reply_to_message_id=current_reply_to,
                allow_sending_without_reply=True,
            )
            return
        except Exception as exc:
            last_exc = exc

    logger.warning(
        f"Не удалось отправить кнопки для просмотра авто в пути пользователю {user_id}, "
        f"source_message_id={source_message_id}: {last_exc}"
    )


def _looks_like_missing_source_message(exc: Exception) -> bool:
    text = str(exc).lower()
    patterns = (
        "message to copy not found",
        "message not found",
        "message_id_invalid",
        "message id invalid",
    )
    return any(pattern in text for pattern in patterns)


async def _delete_auto_in_transit_post_records(channel_id_value: int, message_ids: list[int]) -> int:
    if AutoInTransitPost is None or not message_ids:
        return 0

    deleted_count = 0
    async with async_session() as session:
        result = await session.execute(
            select(AutoInTransitPost).where(
                AutoInTransitPost.channel_id == channel_id_value,
                AutoInTransitPost.message_id.in_(message_ids),
            )
        )
        rows = result.scalars().all()
        if not rows:
            return 0

        for row in rows:
            await session.delete(row)
            deleted_count += 1
        await session.commit()

    return deleted_count


async def clear_auto_in_transit_posts_db(channel_id_value: int | None = None) -> int:
    if AutoInTransitPost is None:
        return 0

    async with async_session() as session:
        query = select(AutoInTransitPost)
        if channel_id_value is not None:
            query = query.where(AutoInTransitPost.channel_id == channel_id_value)
        result = await session.execute(query)
        rows = result.scalars().all()
        if not rows:
            return 0

        for row in rows:
            await session.delete(row)
        await session.commit()
        return len(rows)


async def send_auto_in_transit_post_to_user(
    bot: Bot,
    user_id: int,
    *,
    batch_index: int = 0,
    with_sticker: bool = True,
    _attempt: int = 0,
) -> bool:
    source_channel_id = await get_auto_in_path_channel_id()
    if source_channel_id is None or batch_index < 0:
        return False

    batches = await get_auto_in_transit_copy_batches(newest_first=True)
    if batch_index >= len(batches):
        return False

    if with_sticker:
        await _send_optional_auto_in_path_sticker(bot, user_id)

    message_ids = sorted(batches[batch_index])
    source_message_id = message_ids[0]
    next_post_index = batch_index + 1 if batch_index + 1 < len(batches) else None
    reply_markup = get_auto_in_path_post_keyboard(
        source_channel_id,
        source_message_id,
        next_post_index=next_post_index,
    )

    if len(message_ids) == 1:
        message_id = source_message_id
        try:
            await bot.copy_message(
                chat_id=user_id,
                from_chat_id=source_channel_id,
                message_id=message_id,
                reply_markup=reply_markup,
            )
            return True
        except Exception as exc:
            if _looks_like_missing_source_message(exc):
                removed = await _delete_auto_in_transit_post_records(source_channel_id, [message_id])
                logger.info(
                    f"Удалён отсутствующий пост авто в пути из БД: channel_id={source_channel_id}, "
                    f"message_id={message_id}, removed={removed}"
                )
                if _attempt < 2:
                    return await send_auto_in_transit_post_to_user(
                        bot,
                        user_id,
                        batch_index=batch_index,
                        with_sticker=False,
                        _attempt=_attempt + 1,
                    )
            else:
                logger.error(
                    f"Не удалось скопировать последний пост авто в пути пользователю {user_id}, "
                    f"message_id={message_id}: {exc}"
                )
            return False

    try:
        copied_messages = await bot.copy_messages(
            chat_id=user_id,
            from_chat_id=source_channel_id,
            message_ids=message_ids,
        )
        reply_to_message_id = next(
            (
                copied_id
                for copied_id in (_copied_message_id(item) for item in copied_messages)
                if copied_id is not None
            ),
            None,
        )
        await _send_auto_in_path_actions_prompt(
            bot,
            user_id,
            source_channel_id,
            source_message_id,
            next_post_index=next_post_index,
            reply_to_message_id=reply_to_message_id,
        )
        return True
    except Exception as exc:
        logger.warning(
            f"Ошибка отправки медиа-поста авто в пути пользователю {user_id}, пробую по одному: {exc}"
        )

    first_copied_message = None
    batch_sent = False
    missing_message_ids: list[int] = []
    for message_id in message_ids:
        try:
            copied_message = await bot.copy_message(
                chat_id=user_id,
                from_chat_id=source_channel_id,
                message_id=message_id,
            )
            if first_copied_message is None:
                first_copied_message = copied_message
            batch_sent = True
        except Exception as exc:
            if _looks_like_missing_source_message(exc):
                missing_message_ids.append(message_id)
            else:
                logger.error(
                    f"Не удалось скопировать сообщение авто в пути пользователю {user_id}, "
                    f"message_id={message_id}: {exc}"
                )
        await asyncio.sleep(0.03)

    if missing_message_ids:
        removed = await _delete_auto_in_transit_post_records(source_channel_id, missing_message_ids)
        logger.info(
            f"Удалены отсутствующие сообщения авто в пути из БД: channel_id={source_channel_id}, "
            f"message_ids={missing_message_ids}, removed={removed}"
        )
        if not batch_sent and _attempt < 2:
            return await send_auto_in_transit_post_to_user(
                bot,
                user_id,
                batch_index=batch_index,
                with_sticker=False,
                _attempt=_attempt + 1,
            )

    if not batch_sent:
        return False

    await _send_auto_in_path_actions_prompt(
        bot,
        user_id,
        source_channel_id,
        source_message_id,
        next_post_index=next_post_index,
        reply_to_message_id=_copied_message_id(first_copied_message),
    )
    return True


async def send_auto_in_transit_posts_to_user(bot: Bot, user_id: int) -> int:
    source_channel_id = await get_auto_in_path_channel_id()
    if source_channel_id is None:
        return 0

    batches = await get_auto_in_transit_copy_batches()
    if not batches:
        return 0

    sent_batches = 0
    for message_ids in batches:
        source_message_ids = sorted(message_ids)
        source_message_id = source_message_ids[0]

        if len(source_message_ids) == 1:
            message_id = source_message_id
            try:
                await bot.copy_message(
                    chat_id=user_id,
                    from_chat_id=source_channel_id,
                    message_id=message_id,
                    reply_markup=get_post_actions_keyboard(source_channel_id, message_id),
                )
                sent_batches += 1
            except Exception as exc:
                if _looks_like_missing_source_message(exc):
                    removed = await _delete_auto_in_transit_post_records(source_channel_id, [message_id])
                    logger.info(
                        f"Удалён отсутствующий пост авто в пути из БД: channel_id={source_channel_id}, "
                        f"message_id={message_id}, removed={removed}"
                    )
                else:
                    logger.error(
                        f"Не удалось скопировать сообщение авто в пути пользователю {user_id}, "
                        f"message_id={message_id}: {exc}"
                    )
            await asyncio.sleep(0.05)
            continue

        try:
            copied_messages = await bot.copy_messages(
                chat_id=user_id,
                from_chat_id=source_channel_id,
                message_ids=source_message_ids,
            )
            sent_batches += 1
            attached = False
            for copied_message in copied_messages:
                attached = await _attach_post_actions_keyboard_to_message(
                    bot,
                    user_id,
                    copied_message,
                    source_channel_id,
                    source_message_id,
                    log_failures=False,
                )
                if attached:
                    break

            if not attached:
                reply_to_message_id = next(
                    (
                        copied_id
                        for copied_id in (_copied_message_id(item) for item in copied_messages)
                        if copied_id is not None
                    ),
                    None,
                )
                await _send_post_actions_prompt(
                    bot,
                    user_id,
                    source_channel_id,
                    source_message_id,
                    reply_to_message_id=reply_to_message_id,
                )
        except Exception as exc:
            logger.warning(
                f"Ошибка batch copy авто в пути пользователю {user_id}, пробую по одному: {exc}"
            )
            first_copied_message = None
            batch_sent = False
            for message_id in source_message_ids:
                try:
                    copied_message = await bot.copy_message(
                        chat_id=user_id,
                        from_chat_id=source_channel_id,
                        message_id=message_id,
                    )
                    if first_copied_message is None:
                        first_copied_message = copied_message
                    batch_sent = True
                except Exception as single_exc:
                    if _looks_like_missing_source_message(single_exc):
                        removed = await _delete_auto_in_transit_post_records(source_channel_id, [message_id])
                        logger.info(
                            f"Удалён отсутствующий пост авто в пути из БД: channel_id={source_channel_id}, "
                            f"message_id={message_id}, removed={removed}"
                        )
                    else:
                        logger.error(
                            f"Не удалось скопировать сообщение авто в пути пользователю {user_id}, "
                            f"message_id={message_id}: {single_exc}"
                        )
                await asyncio.sleep(0.03)

            if batch_sent:
                sent_batches += 1
                attached = False
                if first_copied_message is not None:
                    attached = await _attach_post_actions_keyboard_to_message(
                        bot,
                        user_id,
                        first_copied_message,
                        source_channel_id,
                        source_message_id,
                        log_failures=False,
                    )
                if not attached:
                    await _send_post_actions_prompt(
                        bot,
                        user_id,
                        source_channel_id,
                        source_message_id,
                        reply_to_message_id=_copied_message_id(first_copied_message),
                    )
        await asyncio.sleep(0.05)

    return sent_batches


async def notify_admins_new_lead(bot: Bot, lead: Lead) -> None:
    username = getattr(lead, "username", None)
    username_text = f"@{username}" if username else "-"
    created_at = getattr(lead, "created_at", None)
    created_at_text = created_at.strftime("%Y-%m-%d %H:%M:%S") if hasattr(created_at, "strftime") else "-"
    text = (
        "Новый лид\n"
        f"ID лида: {getattr(lead, 'id', '-')}\n"
        f"Действие: {getattr(lead, 'action', '-')}\n"
        f"TG ID: {getattr(lead, 'user_telegram_id', '-')}\n"
        f"Username: {username_text}"
    )
    extra = (
        f"\nИмя: {getattr(lead, 'customer_name', None) or '-'}"
        f"\nТелефон: {getattr(lead, 'phone', None) or '-'}"
        f"\nЦеновая вилка: {getattr(lead, 'price_range', None) or '-'}"
        f"\nКомментарий: {getattr(lead, 'message_text', None) or '-'}"
        f"\nСоздан: {created_at_text} UTC"
    )
    full_text = text + extra

    leads_channel_id = await get_leads_channel_id()
    if leads_channel_id is not None:
        try:
            await bot.send_message(leads_channel_id, full_text)
        except Exception as exc:
            logger.error(f"Не удалось отправить лид в канал {leads_channel_id}: {exc}")

    for admin_id in get_configured_admin_ids(exclude_user_ids={bot.id}):
        if leads_channel_id is not None and admin_id == leads_channel_id:
            continue
        try:
            await bot.send_message(admin_id, full_text)
        except Exception as exc:
            log_admin_delivery_error(admin_id, exc, action="отправить лид")


__all__ = [name for name in globals() if name != "__builtins__"]
