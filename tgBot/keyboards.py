from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from tgBot.catalogs import (
    _get_auto_countries_keyboard,
    _get_auto_engines_keyboard,
    _get_auto_models_keyboard,
    _get_moto_class_display_name,
    _moto_catalog_classes,
)
from tgBot.texts import (
    BACK_BUTTON_TEXT,
    CONTACT_MANAGER_INLINE_TEXT,
    CONTACT_MANAGER_START_INLINE_TEXT,
    CONTACT_MANAGER_TEXT,
    HOME_INLINE_BUTTON_TEXT,
    HOME_REPLY_BUTTON_TEXT,
)

MANAGER_TELEGRAM_URL = "https://t.me/autopartner_import"
CHANNEL_TELEGRAM_URL = "https://t.me/autopartner_by"


def get_user_reply_keyboard() -> types.ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=CONTACT_MANAGER_TEXT)
    kb.button(text=HOME_REPLY_BUTTON_TEXT)
    kb.adjust(1, 1)
    return kb.as_markup(resize_keyboard=True)

def get_post_actions_keyboard(
    source_chat_id: int,
    source_message_id: int,
) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="😍 Нравится",
        callback_data=f"post_like:{source_chat_id}:{source_message_id}",
    )
    kb.adjust(1)
    return kb.as_markup()


def get_auto_in_path_post_keyboard(
    source_chat_id: int,
    source_message_id: int,
    *,
    next_post_index: int | None = None,
) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(
        text="😍 Нравится",
        callback_data=f"post_like:{source_chat_id}:{source_message_id}",
    )
    if next_post_index is not None:
        kb.button(
            text="🚗 Хочу другую",
            callback_data=f"auto_in_path:next:{next_post_index}",
        )
    kb.button(text=HOME_INLINE_BUTTON_TEXT, callback_data="guarantees:home")
    rows = [1]
    if next_post_index is not None:
        rows.append(1)
    rows.append(1)
    kb.adjust(*rows)
    return kb.as_markup()

def get_start_keyboard() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🔥 Актуальные варианты", url=CHANNEL_TELEGRAM_URL)
    #kb.button(text="💯 Максимальная выгода", callback_data="max_profit:open")
    kb.button(text="🔎 Подбор автомобиля", callback_data="lead:auto_pick")
    kb.button(text="🏍️ Подбор мотоцикла", callback_data="lead:moto_pick")
    kb.button(text="⛴ Авто в пути", callback_data="catalog:auto_in_path")
    #kb.button(text="🛡️ Гарантии", callback_data="info:guarantees")
    kb.button(text="❓ Часто задаваемые вопросы", callback_data="info:quick_main")
    kb.button(text=CONTACT_MANAGER_START_INLINE_TEXT, callback_data="lead:contact_manager")
    kb.adjust(1, 1, 1, 1, 1, 1, 1, 1)
    return kb.as_markup()

def get_price_range_keyboard(
    back_callback_data: str = "guarantees:home",
    source: str = "",
) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    source_suffix = f":{source}" if source else ""
    kb.button(text="10 000$ – 16 000$", callback_data=f"price:10_15k{source_suffix}")
    kb.button(text="16 000$ – 20 000$", callback_data=f"price:15_20k{source_suffix}")
    kb.button(text="20 000$ – 30 000$", callback_data=f"price:20_30k{source_suffix}")
    kb.button(text="30 000$+", callback_data=f"price:30k_plus{source_suffix}")
    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(1, 1, 1, 1, 1)
    return kb.as_markup()

def get_auto_countries_keyboard(
    category_id: str,
    back_callback_data: str = "lead:auto_pick",
    source_token: str = "",
) -> types.InlineKeyboardMarkup:
    kb_from_json = _get_auto_countries_keyboard(
        category_id,
        back_callback_data=back_callback_data,
        source_token=source_token,
    )
    if kb_from_json:
        return kb_from_json

    kb = InlineKeyboardBuilder()
    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(1)
    return kb.as_markup()

def get_auto_engines_keyboard(
    category_id: str,
    country_id: str,
    back_callback_data: str = "lead:auto_pick",
    source_token: str = "",
) -> types.InlineKeyboardMarkup:
    kb_from_json = _get_auto_engines_keyboard(
        category_id,
        country_id,
        back_callback_data=back_callback_data,
        source_token=source_token,
    )
    if kb_from_json:
        return kb_from_json

    kb = InlineKeyboardBuilder()
    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(1)
    return kb.as_markup()

def get_auto_engine_models_keyboard(
    category_id: str,
    country_id: str,
    engine_id: str,
    back_callback_data: str = "lead:auto_pick",
    source_token: str = "",
) -> types.InlineKeyboardMarkup:
    kb_from_json = _get_auto_models_keyboard(
        category_id,
        back_callback_data=back_callback_data,
        country_id=country_id,
        engine_id=engine_id,
        source_token=source_token,
    )
    if kb_from_json:
        return kb_from_json

    kb = InlineKeyboardBuilder()
    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(1)
    return kb.as_markup()

def get_auto_in_path_intro_keyboard(
    back_callback_data: str = "guarantees:home",
) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Показать авто в пути", callback_data="catalog:auto_in_path:show")
    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(1, 1)
    return kb.as_markup()

def get_auto_model_actions_keyboard(
    category_id: str,
    model_id: str,
    *,
    country_id: str,
    engine_id: str,
    source_token: str = "",
) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    leave_phone_callback_data = (
        f"auto_model:leave_phone:{category_id}:{country_id}:{engine_id}:{model_id}"
    )
    if source_token:
        leave_phone_callback_data = f"{leave_phone_callback_data}:{source_token}"

    kb.button(text="✉️ Написать менеджеру", url=MANAGER_TELEGRAM_URL)
    kb.button(text="📞 Оставить мой номер телефона", callback_data=leave_phone_callback_data)
    kb.button(text=HOME_INLINE_BUTTON_TEXT, callback_data="guarantees:home")
    kb.adjust(1, 1, 1)
    return kb.as_markup()

def get_manager_contact_keyboard(
    leave_phone_callback_data: str = "lead:contact_manager:phone",
) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✉️ Написать менеджеру", url=MANAGER_TELEGRAM_URL)
    kb.button(text="📞 Оставить мой номер телефона", callback_data=leave_phone_callback_data)
    kb.adjust(1, 1)
    return kb.as_markup()

def get_phone_country_keyboard(
    *,
    back_callback_data: str,
) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🇷🇺 РФ", callback_data="lead_phone_country:ru")
    kb.button(text="🇧🇾 РБ", callback_data="lead_phone_country:by")
    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(1, 1, 1)
    return kb.as_markup()

def get_manual_phone_request_keyboard() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text=HOME_REPLY_BUTTON_TEXT)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )

def get_moto_country_keyboard(
    class_id: str,
    back_callback_data: str = "lead:moto_pick",
) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🇺🇸 США", callback_data=f"moto_country:{class_id}:usa")
    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(1, 1)
    return kb.as_markup()

def get_moto_model_actions_keyboard(class_id: str, model_id: str) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="😍Хочу этот мото", callback_data=f"moto_model:want:{class_id}:{model_id}")
    kb.button(text=HOME_INLINE_BUTTON_TEXT, callback_data="guarantees:home")
    kb.button(text=BACK_BUTTON_TEXT, callback_data=f"moto_country:{class_id}:usa")
    kb.adjust(1, 1, 1)
    return kb.as_markup()

def get_max_profit_keyboard() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="😍Нравится", callback_data="max_profit:want")
    kb.button(text="🚗 Хочу другую", callback_data="max_profit:next")
    kb.button(text=HOME_INLINE_BUTTON_TEXT, callback_data="guarantees:home")
    kb.adjust(1, 1, 1)
    return kb.as_markup()

def get_guarantees_keyboard() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="🧐 А есть риски?", callback_data="guarantees:risks")
    kb.button(text=CONTACT_MANAGER_INLINE_TEXT, callback_data="lead:contact_manager")
    kb.button(text=HOME_INLINE_BUTTON_TEXT, callback_data="guarantees:home")
    kb.button(text=BACK_BUTTON_TEXT, callback_data="guarantees:home")
    kb.adjust(1, 1, 1, 1)
    return kb.as_markup()

def get_guarantees_risks_keyboard() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=CONTACT_MANAGER_INLINE_TEXT, callback_data="lead:contact_manager")
    kb.button(text="🔍 Подобрать авто", callback_data="lead:auto_pick:risks")
    kb.button(text="🏍️ Подобрать мото", callback_data="lead:moto_pick:risks")
    kb.button(text=HOME_INLINE_BUTTON_TEXT, callback_data="guarantees:home")
    kb.button(text=BACK_BUTTON_TEXT, callback_data="info:guarantees")
    kb.adjust(1, 1, 1, 1, 1)
    return kb.as_markup()

def get_quick_main_keyboard() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Какую еще технику можно привезти?", callback_data="quick_main:equipment")
    kb.button(text="Сколько стоят ваши услуги?", callback_data="quick_main:pricing")
    kb.button(text="Какие сроки доставки?", callback_data="quick_main:delivery")
    kb.button(text="Есть ли гарантии?", callback_data="quick_main:guarantees")
    kb.button(text="Где нас найти?", callback_data="quick_main:location")
    kb.button(text=BACK_BUTTON_TEXT, callback_data="guarantees:home")
    kb.adjust(1, 1, 1, 1, 1, 1)
    return kb.as_markup()

def get_quick_main_topic_keyboard(
    *,
    back_callback_data: str = "info:quick_main",
    include_manager: bool = False,
    include_channel: bool = False,
) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    rows: list[int] = []

    if include_manager:
        kb.button(text="✉️ Написать менеджеру", url=MANAGER_TELEGRAM_URL)
        rows.append(1)

    if include_channel:
        kb.button(text="🔥 Актуальные варианты", url=CHANNEL_TELEGRAM_URL)
        rows.append(1)

    kb.button(text=HOME_INLINE_BUTTON_TEXT, callback_data="guarantees:home")
    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    rows.extend([1, 1])
    kb.adjust(*rows)
    return kb.as_markup()

def get_quick_main_auction_keyboard() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=CONTACT_MANAGER_INLINE_TEXT, callback_data="lead:contact_manager")
    kb.button(text="🔍 Подборки авто по ценам", callback_data="lead:auto_pick:quick_main_auction")
    kb.button(text=HOME_INLINE_BUTTON_TEXT, callback_data="guarantees:home")
    kb.button(text=BACK_BUTTON_TEXT, callback_data="info:quick_main")
    kb.adjust(1, 1, 1, 1)
    return kb.as_markup()

def get_quick_main_delivery_keyboard() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=CONTACT_MANAGER_INLINE_TEXT, callback_data="lead:contact_manager")
    kb.button(text="🔍 Подобрать авто", callback_data="lead:auto_pick:quick_main_delivery")
    kb.button(text="🏍️ Подобрать мото", callback_data="lead:moto_pick:quick_main_delivery")
    kb.button(text=HOME_INLINE_BUTTON_TEXT, callback_data="guarantees:home")
    kb.button(text=BACK_BUTTON_TEXT, callback_data="info:quick_main")
    kb.adjust(1, 1, 1, 1, 1)
    return kb.as_markup()

def get_quick_main_credit_keyboard(
    auto_pick_source: str = "quick_main_credit",
) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=CONTACT_MANAGER_INLINE_TEXT, callback_data="lead:contact_manager")
    kb.button(text="🔍 Подборки авто по ценам", callback_data=f"lead:auto_pick:{auto_pick_source}")
    kb.button(text=HOME_INLINE_BUTTON_TEXT, callback_data="guarantees:home")
    kb.button(text=BACK_BUTTON_TEXT, callback_data="info:quick_main")
    kb.adjust(1, 1, 1, 1)
    return kb.as_markup()

def get_moto_classes_keyboard(
    back_callback_data: str = "guarantees:home",
) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    rows = []
    for class_cfg in _moto_catalog_classes():
        class_id = str(class_cfg.get("id", "")).strip()
        button_text = _get_moto_class_display_name(class_id) or str(class_cfg.get("button_text", "")).strip()
        if not class_id or not button_text:
            continue
        kb.button(text=button_text, callback_data=f"moto_class:{class_id}")
        rows.append(1)

    if not rows:
        kb.button(text="5 000$ – 10 000$", callback_data="moto_class:5_10k")
        kb.button(text="10 000$ – 16 000$", callback_data="moto_class:10_15k")
        kb.button(text="16 000$ – 20 000$", callback_data="moto_class:15_20k")
        kb.button(text="20 000$ – 30 000$", callback_data="moto_class:20_30k")
        rows = [1, 1, 1, 1]

    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    rows.append(1)
    kb.adjust(*rows)
    return kb.as_markup()

def get_admin_keyboard() -> types.ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Статистика пользователей")
    kb.button(text="Последние лиды")
    kb.button(text="Канал авто в пути")
    kb.button(text="Канал лидов")
    kb.adjust(1, 1, 1, 1)
    return kb.as_markup(resize_keyboard=True)

def get_contact_request_keyboard() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📱 Отправить номер", request_contact=True)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
