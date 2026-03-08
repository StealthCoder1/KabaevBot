from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder

from tgBot.catalogs import _get_auto_models_keyboard, _moto_catalog_classes
from tgBot.texts import (
    BACK_BUTTON_TEXT,
    CONTACT_MANAGER_INLINE_TEXT,
    CONTACT_MANAGER_START_INLINE_TEXT,
    CONTACT_MANAGER_TEXT,
    HOME_INLINE_BUTTON_TEXT,
    HOME_REPLY_BUTTON_TEXT,
)


def get_user_reply_keyboard() -> types.ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text=CONTACT_MANAGER_TEXT)
    kb.button(text=HOME_REPLY_BUTTON_TEXT)
    kb.adjust(1, 1)
    return kb.as_markup(resize_keyboard=True)

def get_post_actions_keyboard() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text=CONTACT_MANAGER_TEXT, callback_data="lead:contact_manager")
    kb.adjust(1)
    return kb.as_markup()

def get_start_keyboard() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="💯 Максимальная выгода", callback_data="max_profit:open")
    kb.button(text="🔎 Подборка авто", callback_data="lead:auto_pick")
    kb.button(text="🏍️ Подборка мото", callback_data="lead:moto_pick")
    kb.button(text="🚗 Авто в пути", callback_data="catalog:auto_in_path")
    kb.button(text="🛡️ Гарантии", callback_data="info:guarantees")
    kb.button(text="❓ Быстро о главном", callback_data="info:quick_main")
    kb.button(text=CONTACT_MANAGER_START_INLINE_TEXT, callback_data="lead:contact_manager")
    kb.adjust(1, 1, 1, 1, 1, 1, 1)
    return kb.as_markup()

def get_price_range_keyboard(
    back_callback_data: str = "guarantees:home",
    source: str = "",
) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    source_suffix = f":{source}" if source else ""
    kb.button(text="👉 9 000$ - 12 000$", callback_data=f"price:9_12k{source_suffix}")
    kb.button(text="👉 12 000$ - 15 000$", callback_data=f"price:12_15k{source_suffix}")
    kb.button(text="👉 15 000$ - 20 000$", callback_data=f"price:15_20k{source_suffix}")
    kb.button(text="👉 20 000$ - 30 000$", callback_data=f"price:20_30k{source_suffix}")
    kb.button(text="👉 30 000$+ (люкс)", callback_data=f"price:30k_plus_lux{source_suffix}")
    kb.button(text="😍 Самые выгодные авто", callback_data=f"price:best_deals{source_suffix}")
    kb.button(text="😍 Электрокары", callback_data=f"price:electric{source_suffix}")
    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(1, 1, 1, 1, 1, 1, 1, 1, 1)
    return kb.as_markup()

def get_budget_9_12_models_keyboard(
    back_callback_data: str = "lead:auto_pick",
) -> types.InlineKeyboardMarkup:
    kb_from_json = _get_auto_models_keyboard("9_12k", back_callback_data=back_callback_data)
    if kb_from_json:
        return kb_from_json

    kb = InlineKeyboardBuilder()
    kb.button(text="Chevrolet Trax", callback_data="budget9_12:model:trax")
    kb.button(text="Chevrolet Malibu", callback_data="budget9_12:model:malibu")
    kb.button(text="Ford Ecosport", callback_data="budget9_12:model:ecosport")
    kb.button(text="Ford Escape", callback_data="budget9_12:model:escape")
    kb.button(text="Chevrolet Trailblazer", callback_data="budget9_12:model:trailblazer")
    kb.button(text="Buick Encore GX", callback_data="budget9_12:model:encore_gx")
    kb.button(text="Chevrolet Equinox (дорест)", callback_data="budget9_12:model:equinox_pre")
    kb.button(text="Volkswagen Jetta", callback_data="budget9_12:model:jetta")
    kb.button(text="Mini Cooper", callback_data="budget9_12:model:mini_cooper")
    kb.button(text="Mitsubishi Mirage", callback_data="budget9_12:model:mirage")
    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(2, 2, 1, 1, 1, 1, 1, 1, 1)
    return kb.as_markup()

def get_budget_12_15_models_keyboard(
    back_callback_data: str = "lead:auto_pick",
) -> types.InlineKeyboardMarkup:
    kb_from_json = _get_auto_models_keyboard("12_15k", back_callback_data=back_callback_data)
    if kb_from_json:
        return kb_from_json

    kb = InlineKeyboardBuilder()
    kb.button(text="GMC Terrain", callback_data="budget12_15:model:terrain")
    kb.button(text="Honda Civic", callback_data="budget12_15:model:civic")
    kb.button(text="Honda Accord", callback_data="budget12_15:model:accord")
    kb.button(text="Chevrolet Equinox", callback_data="budget12_15:model:equinox")
    kb.button(text="Fiat 124 Spider", callback_data="budget12_15:model:fiat_124_spider")
    kb.button(text="Ford Bronco Sport", callback_data="budget12_15:model:bronco_sport")
    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(1, 1, 1, 1, 1, 1, 1)
    return kb.as_markup()

def get_budget_15_20_models_keyboard(
    back_callback_data: str = "lead:auto_pick",
) -> types.InlineKeyboardMarkup:
    kb_from_json = _get_auto_models_keyboard("15_20k", back_callback_data=back_callback_data)
    if kb_from_json:
        return kb_from_json

    kb = InlineKeyboardBuilder()
    kb.button(text="Lincoln Corsair", callback_data="budget15_20:model:corsair")
    kb.button(text="Buick Envision", callback_data="budget15_20:model:envision")
    kb.button(text="Buick Encore", callback_data="budget15_20:model:encore")
    kb.button(text="BMW 4 Series", callback_data="budget15_20:model:bmw_4_series")
    kb.button(text="Audi Q7", callback_data="budget15_20:model:audi_q7")
    kb.button(text="Volvo S60", callback_data="budget15_20:model:volvo_s60")
    kb.button(text="Tesla Model 3", callback_data="budget15_20:model:tesla_model_3")
    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(1, 1, 1, 1, 1, 1, 1, 1)
    return kb.as_markup()

def get_budget_20_30_models_keyboard(
    back_callback_data: str = "lead:auto_pick",
) -> types.InlineKeyboardMarkup:
    kb_from_json = _get_auto_models_keyboard("20_30k", back_callback_data=back_callback_data)
    if kb_from_json:
        return kb_from_json

    kb = InlineKeyboardBuilder()
    kb.button(text="Ford Explorer", callback_data="budget20_30:model:explorer")
    kb.button(text="BMW X5", callback_data="budget20_30:model:bmw_x5")
    kb.button(text="Audi A4", callback_data="budget20_30:model:audi_a4")
    kb.button(text="Chrysler Pacifica", callback_data="budget20_30:model:pacifica")
    kb.button(text="Jaguar F-Pace", callback_data="budget20_30:model:f_pace")
    kb.button(text="Range Rover Evoque", callback_data="budget20_30:model:evoque")
    kb.button(text="Hyundai Santa Fe", callback_data="budget20_30:model:santa_fe")
    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(1, 1, 1, 1, 1, 1, 1, 1)
    return kb.as_markup()

def get_budget_30k_plus_models_keyboard(
    back_callback_data: str = "lead:auto_pick",
) -> types.InlineKeyboardMarkup:
    kb_from_json = _get_auto_models_keyboard("30k_plus_lux", back_callback_data=back_callback_data)
    if kb_from_json:
        return kb_from_json

    kb = InlineKeyboardBuilder()
    kb.button(text="Chevrolet Corvette", callback_data="budget30k_plus:model:corvette")
    kb.button(text="Ford Mustang", callback_data="budget30k_plus:model:mustang")
    kb.button(text="GMC Acadia", callback_data="budget30k_plus:model:acadia")
    kb.button(text="BMW M4", callback_data="budget30k_plus:model:bmw_m4")
    kb.button(text="Bentley Bentayga", callback_data="budget30k_plus:model:bentayga")
    kb.button(text="Porsche Taycan", callback_data="budget30k_plus:model:taycan")
    kb.button(text="Audi A5", callback_data="budget30k_plus:model:audi_a5")
    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(1, 1, 1, 1, 1, 1, 1, 1)
    return kb.as_markup()

def get_best_deals_keyboard() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="✅ Хочу авто из подборки", callback_data="best_deals:want")
    kb.button(text="🚗Другие авто с выгодой", callback_data="best_deals:other")
    kb.button(text=CONTACT_MANAGER_INLINE_TEXT, callback_data="lead:contact_manager")
    kb.button(text=HOME_REPLY_BUTTON_TEXT, callback_data="guarantees:home")
    kb.button(text=BACK_BUTTON_TEXT, callback_data="best_deals:back")
    kb.adjust(1, 1, 1, 1, 1)
    return kb.as_markup()

def get_electric_models_keyboard(
    back_callback_data: str = "lead:auto_pick",
) -> types.InlineKeyboardMarkup:
    kb_from_json = _get_auto_models_keyboard("electric", back_callback_data=back_callback_data)
    if kb_from_json:
        return kb_from_json

    kb = InlineKeyboardBuilder()
    kb.button(text="Hyundai Kona EV", callback_data="electric:model:kona_ev")
    kb.button(text="Smart Fortwo Electric", callback_data="electric:model:smart_fortwo_electric")
    kb.button(text="Hyundai Ioniq 5", callback_data="electric:model:ioniq_5")
    kb.button(text="Chevrolet Bolt EV", callback_data="electric:model:bolt_ev")
    kb.button(text="Chevrolet Spark EV", callback_data="electric:model:spark_ev")
    kb.button(text="Tesla Model 3", callback_data="electric:model:tesla_model_3")
    kb.button(text="BMW i3", callback_data="electric:model:bmw_i3")
    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(1, 1, 1, 1, 1, 1, 1, 1)
    return kb.as_markup()

def get_auto_model_actions_keyboard(category_id: str, model_id: str) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="😍Хочу это авто", callback_data=f"auto_model:want:{category_id}:{model_id}")
    kb.button(text=HOME_INLINE_BUTTON_TEXT, callback_data="guarantees:home")
    kb.button(text=BACK_BUTTON_TEXT, callback_data=f"price:{category_id}")
    kb.adjust(1, 1, 1)
    return kb.as_markup()

def get_moto_model_actions_keyboard(class_id: str, model_id: str) -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="😍Хочу этот мото", callback_data=f"moto_model:want:{class_id}:{model_id}")
    kb.button(text=HOME_INLINE_BUTTON_TEXT, callback_data="guarantees:home")
    kb.button(text=BACK_BUTTON_TEXT, callback_data=f"moto_class:{class_id}")
    kb.adjust(1, 1, 1)
    return kb.as_markup()

def get_max_profit_keyboard() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="😍Хочу это авто", callback_data="max_profit:want")
    kb.button(text="💯смотреть дальше", callback_data="max_profit:next")
    kb.button(text=HOME_INLINE_BUTTON_TEXT, callback_data="guarantees:home")
    kb.button(text=BACK_BUTTON_TEXT, callback_data="guarantees:home")
    kb.adjust(1, 1, 1, 1)
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
    kb.button(text="🚗Покупка авто на аукционе", callback_data="quick_main:auction")
    kb.button(text="🛳️Сколько едет авто из США?", callback_data="quick_main:delivery")
    kb.button(text="💵 Кредит/лизинг", callback_data="quick_main:credit")
    kb.button(text="🛡️ Авто страхуется?", callback_data="quick_main:insurance")
    kb.button(text="🛠️ Скрытые повреждения", callback_data="quick_main:hidden_damage")
    kb.button(text=HOME_INLINE_BUTTON_TEXT, callback_data="guarantees:home")
    kb.button(text=BACK_BUTTON_TEXT, callback_data="guarantees:home")
    kb.adjust(1, 1, 1, 1, 1, 1, 1)
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
        button_text = str(class_cfg.get("button_text", "")).strip()
        if not class_id or not button_text:
            continue
        kb.button(text=button_text, callback_data=f"moto_class:{class_id}")
        rows.append(1)

    if not rows:
        kb.button(text="🏁 Спорт", callback_data="moto_class:sport")
        kb.button(text="🏙️ Стрит", callback_data="moto_class:street")
        kb.button(text="🛣️ Крузер", callback_data="moto_class:cruiser")
        rows = [1, 1, 1]

    kb.button(text=HOME_INLINE_BUTTON_TEXT, callback_data="guarantees:home")
    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    rows.extend([1, 1])
    kb.adjust(*rows)
    return kb.as_markup()

def get_moto_sport_models_keyboard() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="CBR1000rr от 2008 года", callback_data="moto_sport:model:cbr1000rr_2008")
    kb.button(text="Suzuki GSX-R600\\750", callback_data="moto_sport:model:gsxr_600_750")
    kb.button(text="Suzuki Hayabusa от 2022", callback_data="moto_sport:model:hayabusa_2022")
    kb.button(text="Kawasaki ZX10RR от 2020", callback_data="moto_sport:model:zx10rr_2020")
    kb.button(text="Yamaha R1 от 2018", callback_data="moto_sport:model:yamaha_r1_2018")
    kb.button(text="Aprillia RSV4 от 2020", callback_data="moto_sport:model:rsv4_2020")
    kb.button(text="BMW S1000RR от 2019", callback_data="moto_sport:model:s1000rr_2019")
    kb.button(text="Ducati Panigale V4 от 2023", callback_data="moto_sport:model:panigale_v4_2023")
    kb.button(text=BACK_BUTTON_TEXT, callback_data="lead:moto_pick")
    kb.adjust(1, 1, 1, 1, 1, 1, 1, 1, 1)
    return kb.as_markup()

def get_moto_street_models_keyboard() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Kawasaki Z900 2017", callback_data="moto_street:model:z900_2017")
    kb.button(text="Yamaha MT09", callback_data="moto_street:model:mt09")
    kb.button(text="Yamaha MT10", callback_data="moto_street:model:mt10")
    kb.button(text="Aprilia Tuono V4 от 2020", callback_data="moto_street:model:tuono_v4_2020")
    kb.button(
        text="Ducati Streetfighter V4 от 2020",
        callback_data="moto_street:model:streetfighter_v4_2020",
    )
    kb.button(text="Kawasaki ZH2", callback_data="moto_street:model:zh2")
    kb.button(text=BACK_BUTTON_TEXT, callback_data="lead:moto_pick")
    kb.adjust(1, 1, 1, 1, 1, 1, 1)
    return kb.as_markup()

def get_moto_cruiser_models_keyboard() -> types.InlineKeyboardMarkup:
    kb = InlineKeyboardBuilder()
    kb.button(text="Honda VT750 от 2024", callback_data="moto_cruiser:model:vt750_2024")
    kb.button(
        text="Harley Davidson FatBoy",
        callback_data="moto_cruiser:model:harley_fatboy",
    )
    kb.button(
        text="Ducati XDiavel 1260 2017",
        callback_data="moto_cruiser:model:xdiavel_1260_2017",
    )
    kb.button(text=BACK_BUTTON_TEXT, callback_data="lead:moto_pick")
    kb.adjust(1, 1, 1, 1)
    return kb.as_markup()

def get_admin_keyboard() -> types.ReplyKeyboardMarkup:
    kb = ReplyKeyboardBuilder()
    kb.button(text="Статистика пользователей")
    kb.button(text="Последние лиды")
    kb.button(text="Канал авто в пути")
    kb.button(text="Канал лидов")
    kb.button(text=HOME_REPLY_BUTTON_TEXT)
    kb.adjust(1, 1, 1, 1, 1)
    return kb.as_markup(resize_keyboard=True)

def get_contact_request_keyboard() -> types.ReplyKeyboardMarkup:
    return types.ReplyKeyboardMarkup(
        keyboard=[
            [types.KeyboardButton(text="📱 Отправить номер", request_contact=True)],
            [types.KeyboardButton(text=HOME_REPLY_BUTTON_TEXT)],
        ],
        resize_keyboard=True,
        one_time_keyboard=True,
    )
