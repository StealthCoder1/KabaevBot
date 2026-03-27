from tgBot.bot.shared import *


AUTO_PICK_SOURCE_TO_TOKEN = {
    "risks": "r",
    "quick_main_auction": "qa",
    "quick_main_delivery": "qd",
    "quick_main_credit": "qc",
    "quick_main_insurance": "qi",
    "quick_main_hidden_damage": "qhd",
}
AUTO_PICK_TOKEN_TO_SOURCE = {token: source for source, token in AUTO_PICK_SOURCE_TO_TOKEN.items()}
AUTO_BUDGET_HEADLINE_LABELS = {
    "9_12k": "9–12k$",
    "12_15k": "12–15k$",
    "15_20k": "15–20k$",
    "20_30k": "20–30k$",
    "30k_plus_lux": "30k$+",
}
AUTO_BUDGET_MODELS_BODY = (
    "👇 Выбирайте модель — и смотрите, за сколько мы реально\n"
    "привозим такие авто нашим клиентам.\n"
    "P.S. цены ниже рынка РБ до 40%\n\n"
    "❕ Часто цена зависит от множества факторов и даже одна и\n"
    "та же модель с одинаковым годом может стоить по-разному,\n"
    "потому что:\n"
    "1) степень повреждений\n"
    "2) пробег\n"
    "3) комплектации\n"
    "Мы ориентируемся на статистику\n\n"
    "Начнём? Жмите кнопку ниже 👇"
)


def _source_to_token(source: str) -> str:
    return AUTO_PICK_SOURCE_TO_TOKEN.get(source, "")


def _token_to_source(source_token: str) -> str:
    return AUTO_PICK_TOKEN_TO_SOURCE.get(source_token, "")


def _get_auto_pick_callback_data(source: str) -> str:
    return f"lead:auto_pick:{source}" if source else "lead:auto_pick"


def _get_price_callback_data(category_id: str, source: str = "") -> str:
    return f"price:{category_id}:{source}" if source else f"price:{category_id}"


def _get_price_country_callback_data(
    category_id: str,
    country_id: str,
    source_token: str = "",
) -> str:
    callback_data = f"price_country:{category_id}:{country_id}"
    if source_token:
        callback_data = f"{callback_data}:{source_token}"
    return callback_data


def _get_auto_budget_intro_text(category_id: str, country_title: str | None = None) -> str:
    label = AUTO_BUDGET_HEADLINE_LABELS.get(category_id, _get_auto_category_label(category_id))
    headline = f"🔥 Лучшие авто в бюджете {label}"
    if country_title:
        headline = f"{headline} / {country_title}"
    return f"{headline}\n{AUTO_BUDGET_MODELS_BODY}"


async def _show_country_picker(
    callback: types.CallbackQuery,
    *,
    category_id: str,
    source: str = "",
) -> None:
    category_label = _get_auto_category_label(category_id)
    await callback.message.answer(
        f"🌍 Выберите страну для бюджета {category_label}",
        reply_markup=get_auto_countries_keyboard(
            category_id,
            back_callback_data=_get_auto_pick_callback_data(source),
            source_token=_source_to_token(source),
        ),
    )


async def _show_legacy_budget_model_card(
    callback: types.CallbackQuery,
    *,
    category_id: str,
) -> None:
    model_id = _extract_model_id(callback.data)
    country_id = _get_auto_model_country_id(category_id, model_id)
    back_callback_data = (
        _get_price_country_callback_data(category_id, country_id)
        if country_id
        else _get_price_callback_data(category_id)
    )
    await _show_auto_model_card(
        callback,
        category_id=category_id,
        country_id=country_id,
        model_id=model_id,
        back_callback_data=back_callback_data,
    )


@router.callback_query((F.data == "lead:auto_pick") | F.data.startswith("lead:auto_pick:"))
async def auto_pick_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    parts = callback.data.split(":", maxsplit=2)
    source = parts[2] if len(parts) == 3 else ""
    back_callback_data = {
        "risks": "guarantees:risks",
        "quick_main_auction": "quick_main:auction",
        "quick_main_delivery": "quick_main:delivery",
        "quick_main_credit": "quick_main:credit",
        "quick_main_insurance": "quick_main:insurance",
        "quick_main_hidden_damage": "quick_main:hidden_damage",
    }.get(source, "guarantees:home")
    await callback.message.answer(
        BUDGET_PROMPT_TEXT,
        reply_markup=get_price_range_keyboard(
            back_callback_data=back_callback_data,
            source=source,
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("price:"))
async def price_range_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    parts = callback.data.split(":", maxsplit=2)
    payload = parts[1] if len(parts) > 1 else ""
    source = parts[2] if len(parts) == 3 else ""
    auto_pick_callback_data = _get_auto_pick_callback_data(source)

    if payload == "cancel":
        await callback.message.answer("Выбор цены отменен.")
        await callback.answer()
        return

    if _auto_category_has_countries(payload):
        await _show_country_picker(callback, category_id=payload, source=source)
        await callback.answer()
        return

    if payload == "electric":
        await callback.message.answer(
            "🔥 Лучшие и набирающие обороты \"электрички\".\n"
            "Комфортно. Выгодно.\n\n"
            "👇 Выбирайте модель — и смотрите, за сколько мы реально\n"
            "привозим такие авто нашим клиентам.\n"
            "P.S. цены ниже рынка РБ до 40%\n\n"
            "❕ Часто цена зависит от множества факторов и даже одна и\n"
            "та же модель с одинаковым годом может стоить по-разному,\n"
            "потому что:\n"
            "1) степень повреждений\n"
            "2) пробег\n"
            "3) комплектации\n"
            "Мы ориентируемся на статистику\n\n"
            "Начнём? Жмите кнопку ниже 👇",
            reply_markup=get_electric_models_keyboard(back_callback_data=auto_pick_callback_data),
        )
        await callback.answer()
        return

    if payload == "best_deals":
        await callback.message.answer(
            "🔥 Есть тачки, на которых можно не просто сэкономить, а\n"
            "реально заработать.\n\n"
            "В РБ они стоят минимум на 5 000$ дороже, а максимум\n"
            "бесконечен... продавцы вторички в последнее время\n"
            "состязаются в удивительности цен и своих\n"
            "предпринимательских навыках, да? ;)\n\n"
            "Привёз из США — покатался — и продал в плюс.\n"
            "Это как вложение, только ещё и кайфуете за рулём.\n\n"
            "Звучит прибыльно? 💰 Жмите \"связаться с менеджером\" и\n"
            "давайте выберем для вас лучшую тачку 👇",
            reply_markup=get_best_deals_keyboard(),
        )
        await callback.answer()
        return

    await callback.message.answer(
        "Подборка в пути — загружается, пару секунд! ⌛\n\n"
        "Мы собрали для вас самые ходовые варианты в этом бюджете."
    )
    await callback.answer()


@router.callback_query(F.data.startswith("price_country:"))
async def price_country_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    parts = callback.data.split(":")
    if len(parts) not in (3, 4):
        await callback.answer(_get_auto_model_placeholder_text())
        return

    _, category_id, country_id, *rest = parts
    source_token = rest[0] if rest else ""
    source = _token_to_source(source_token)
    country_title = _get_auto_country_title(category_id, country_id) or country_id

    await callback.message.answer(
        _get_auto_budget_intro_text(category_id, country_title),
        reply_markup=get_auto_country_models_keyboard(
            category_id,
            country_id,
            back_callback_data=_get_price_callback_data(category_id, source),
            source_token=source_token,
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("auto_model_pick:"))
async def auto_model_pick_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    parts = callback.data.split(":")
    if len(parts) not in (4, 5):
        await callback.answer(_get_auto_model_placeholder_text())
        return

    _, category_id, country_id, model_id, *rest = parts
    source_token = rest[0] if rest else ""
    await _show_auto_model_card(
        callback,
        category_id=category_id,
        country_id=country_id,
        model_id=model_id,
        back_callback_data=_get_price_country_callback_data(category_id, country_id, source_token),
        source_token=source_token,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("budget9_12:model:"))
async def budget_9_12_model_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    await _show_legacy_budget_model_card(callback, category_id="9_12k")
    await callback.answer()


@router.callback_query(F.data.startswith("budget12_15:model:"))
async def budget_12_15_model_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    await _show_legacy_budget_model_card(callback, category_id="12_15k")
    await callback.answer()


@router.callback_query(F.data.startswith("budget15_20:model:"))
async def budget_15_20_model_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    await _show_legacy_budget_model_card(callback, category_id="15_20k")
    await callback.answer()


@router.callback_query(F.data.startswith("budget20_30:model:"))
async def budget_20_30_model_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    await _show_legacy_budget_model_card(callback, category_id="20_30k")
    await callback.answer()


@router.callback_query(F.data.startswith("budget30k_plus:model:"))
async def budget_30k_plus_model_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    await _show_legacy_budget_model_card(callback, category_id="30k_plus_lux")
    await callback.answer()


@router.callback_query(F.data.startswith("electric:model:"))
async def electric_model_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    await _show_auto_model_card(
        callback,
        category_id="electric",
        model_id=_extract_model_id(callback.data),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("auto_model:want:"))
async def auto_model_want_callback(callback: types.CallbackQuery, state: FSMContext):
    await ensure_user_exists(callback.from_user)
    parts = callback.data.split(":")
    if len(parts) < 4:
        await callback.answer(_get_auto_model_placeholder_text())
        return

    category_id = parts[2]
    country_id = None

    if _auto_category_has_countries(category_id) and len(parts) >= 5:
        country_id = parts[3]
        model_id = parts[4]
    else:
        model_id = parts[3]

    model_title = (
        _get_auto_model_lead_message(category_id, model_id, country_id=country_id)
        or _get_auto_model_title(category_id, model_id, country_id=country_id)
        or model_id
    )
    price_range_label = _get_auto_category_label(category_id)
    if country_id:
        country_title = _get_auto_country_title(category_id, country_id) or country_id
        price_range_label = f"{price_range_label} / {country_title}"

    await state.set_state(LeadStates.waiting_contact)
    await state.update_data(
        pending_lead_action="auto_model_want",
        pending_lead_message_text=model_title,
        pending_lead_price_range=price_range_label,
        pending_back_target="auto_pick",
    )
    await callback.message.answer(
        "📱 Отправьте номер телефона — и стартуем с подбором",
        reply_markup=types.ReplyKeyboardRemove(),
    )
    await callback.answer()


@router.callback_query(F.data == "best_deals:want")
async def best_deals_want_callback(
    callback: types.CallbackQuery, bot: Bot, state: FSMContext
):
    await ensure_user_exists(callback.from_user)
    await state.set_state(LeadStates.waiting_contact)
    await state.update_data(
        pending_lead_action="best_deals_want",
        pending_lead_message_text=None,
        pending_lead_price_range=None,
        pending_back_target="best_deals",
    )
    await callback.message.answer(LEAD_CONTACT_REQUEST_TEXT, reply_markup=get_contact_request_keyboard())
    await callback.answer()


@router.callback_query(F.data == "best_deals:other")
async def best_deals_other_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    await callback.message.answer(
        BUDGET_PROMPT_TEXT, reply_markup=get_price_range_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "best_deals:back")
async def best_deals_back_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    await callback.message.answer(
        BUDGET_PROMPT_TEXT, reply_markup=get_price_range_keyboard()
    )
    await callback.answer()


@router.callback_query(F.data == "max_profit:open")
async def max_profit_open_callback(callback: types.CallbackQuery, state: FSMContext):
    await ensure_user_exists(callback.from_user)
    await _send_random_max_profit_lot(callback, state)
    await callback.answer()


@router.callback_query(F.data == "max_profit:want")
async def max_profit_want_callback(
    callback: types.CallbackQuery, bot: Bot, state: FSMContext
):
    await ensure_user_exists(callback.from_user)
    lot_title = (await state.get_data()).get("max_profit_lot_title") or "Выгодный лот"
    await state.set_state(LeadStates.waiting_contact)
    await state.update_data(
        pending_lead_action="max_profit_want",
        pending_lead_message_text=lot_title,
        pending_lead_price_range=None,
        pending_back_target="home",
    )
    await callback.message.answer(LEAD_CONTACT_REQUEST_TEXT, reply_markup=get_contact_request_keyboard())
    await callback.answer()


@router.callback_query(F.data == "max_profit:next")
async def max_profit_next_callback(callback: types.CallbackQuery, state: FSMContext):
    await ensure_user_exists(callback.from_user)
    await _send_random_max_profit_lot(callback, state, exclude_current=True)
    await callback.answer()
