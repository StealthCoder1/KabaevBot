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
AUTO_BUDGET_MODELS_BODY = (
    "Перед вами список, который подходят под заданные параметры.\n"
    "Важно: цена на одинаковые модели и годы выпуска может существенно различаться. "
    "Это зависит от нескольких ключевых факторов:\n"
    "•  степень повреждения,\n"
    "•  пробег,\n"
    "•  комплектация."
)
AUTO_BUDGET_MODELS_FOOTER = "Мы опираемся только на статистику, а значит — на реальные цифры, а не на догадки!"
MANUAL_PHONE_FLOW_STATES = {
    LeadStates.waiting_phone_country.state,
    LeadStates.waiting_manual_phone.state,
}


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


def _get_price_engine_callback_data(
    category_id: str,
    country_id: str,
    engine_id: str,
    source_token: str = "",
) -> str:
    callback_data = f"price_engine:{category_id}:{country_id}:{engine_id}"
    if source_token:
        callback_data = f"{callback_data}:{source_token}"
    return callback_data


def _get_auto_model_pick_callback_data(
    category_id: str,
    country_id: str,
    engine_id: str,
    model_id: str,
    source_token: str = "",
) -> str:
    callback_data = f"auto_model_pick:{category_id}:{country_id}:{engine_id}:{model_id}"
    if source_token:
        callback_data = f"{callback_data}:{source_token}"
    return callback_data


def _build_auto_price_range_label(
    category_id: str,
    country_id: str,
    engine_id: str,
) -> str:
    category_label = _get_auto_category_label(category_id)
    country_title = _get_auto_country_title(category_id, country_id) or country_id
    engine_title = _get_auto_engine_title(category_id, country_id, engine_id) or engine_id
    return f"{category_label} / {country_title} / {engine_title}"


def _get_auto_budget_intro_text(
    category_id: str,
    *,
    country_title: str | None = None,
    engine_title: str | None = None,
) -> str:
    lines = [f"Бюджет: <b>{_get_auto_category_label(category_id)}</b>"]
    if engine_title:
        lines.append(f"Топливо: <b>{engine_title.lower()}</b>")
    lines.append(AUTO_BUDGET_MODELS_BODY)
    lines.append(f"<b>{AUTO_BUDGET_MODELS_FOOTER}</b>")
    return "\n".join(lines)


async def _clear_manual_phone_state_if_needed(state: FSMContext) -> None:
    current_state = await state.get_state()
    if current_state in MANUAL_PHONE_FLOW_STATES:
        await state.clear()


async def _show_country_picker(
    callback: types.CallbackQuery,
    *,
    category_id: str,
    source: str = "",
) -> None:
    await callback.message.answer(
        "<b>Из какой страны рассматриваете автомобиль?</b>",
        parse_mode="HTML",
        reply_markup=get_auto_countries_keyboard(
            category_id,
            back_callback_data=_get_auto_pick_callback_data(source),
            source_token=_source_to_token(source),
        ),
    )


@router.callback_query((F.data == "lead:auto_pick") | F.data.startswith("lead:auto_pick:"))
async def auto_pick_callback(callback: types.CallbackQuery, state: FSMContext):
    await ensure_user_exists(callback.from_user)
    await _clear_manual_phone_state_if_needed(state)
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
        parse_mode="HTML",
        reply_markup=get_price_range_keyboard(
            back_callback_data=back_callback_data,
            source=source,
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("price:"))
async def price_range_callback(callback: types.CallbackQuery, state: FSMContext):
    await ensure_user_exists(callback.from_user)
    await _clear_manual_phone_state_if_needed(state)
    parts = callback.data.split(":", maxsplit=2)
    payload = parts[1] if len(parts) > 1 else ""
    source = parts[2] if len(parts) == 3 else ""

    if payload == "cancel":
        await callback.message.answer("Выбор бюджета отменен.")
        await callback.answer()
        return

    if not _auto_category_has_countries(payload):
        await callback.answer(_get_auto_model_placeholder_text())
        return

    await _show_country_picker(callback, category_id=payload, source=source)
    await callback.answer()


@router.callback_query(F.data.startswith("price_country:"))
async def price_country_callback(callback: types.CallbackQuery, state: FSMContext):
    await ensure_user_exists(callback.from_user)
    await _clear_manual_phone_state_if_needed(state)
    parts = callback.data.split(":")
    if len(parts) not in (3, 4):
        await callback.answer(_get_auto_model_placeholder_text())
        return

    _, category_id, country_id, *rest = parts
    source_token = rest[0] if rest else ""
    source = _token_to_source(source_token)

    await callback.message.answer(
        "<b>Выберите тип двигателя</b>",
        parse_mode="HTML",
        reply_markup=get_auto_engines_keyboard(
            category_id,
            country_id,
            back_callback_data=_get_price_callback_data(category_id, source),
            source_token=source_token,
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("price_engine:"))
async def price_engine_callback(callback: types.CallbackQuery, state: FSMContext):
    await ensure_user_exists(callback.from_user)
    await _clear_manual_phone_state_if_needed(state)
    parts = callback.data.split(":")
    if len(parts) not in (4, 5):
        await callback.answer(_get_auto_model_placeholder_text())
        return

    _, category_id, country_id, engine_id, *rest = parts
    source_token = rest[0] if rest else ""
    country_title = _get_auto_country_title(category_id, country_id) or country_id
    engine_title = _get_auto_engine_title(category_id, country_id, engine_id) or engine_id

    await callback.message.answer(
        _get_auto_budget_intro_text(
            category_id,
            country_title=country_title,
            engine_title=engine_title,
        ),
        parse_mode="HTML",
        reply_markup=get_auto_engine_models_keyboard(
            category_id,
            country_id,
            engine_id,
            back_callback_data=_get_price_country_callback_data(category_id, country_id, source_token),
            source_token=source_token,
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("auto_model_pick:"))
async def auto_model_pick_callback(callback: types.CallbackQuery, state: FSMContext):
    await ensure_user_exists(callback.from_user)
    await _clear_manual_phone_state_if_needed(state)
    parts = callback.data.split(":")
    if len(parts) not in (5, 6):
        await callback.answer(_get_auto_model_placeholder_text())
        return

    _, category_id, country_id, engine_id, model_id, *rest = parts
    source_token = rest[0] if rest else ""
    await _show_auto_model_card(
        callback,
        category_id=category_id,
        country_id=country_id,
        engine_id=engine_id,
        model_id=model_id,
        source_token=source_token,
    )
    await callback.answer()


@router.callback_query(F.data.startswith("auto_model:contact_manager:"))
async def auto_model_contact_manager_callback(callback: types.CallbackQuery, state: FSMContext):
    await ensure_user_exists(callback.from_user)
    parts = callback.data.split(":")
    leave_phone_callback_data = "lead:contact_manager:phone"
    if len(parts) >= 6:
        _, _, category_id, country_id, engine_id, model_id, *rest = parts
        leave_phone_callback_data = (
            f"auto_model:leave_phone:{category_id}:{country_id}:{engine_id}:{model_id}"
        )
        if rest:
            leave_phone_callback_data = f"{leave_phone_callback_data}:{rest[0]}"

    await callback.message.answer(
        "<b>Выберите способ связи с менеджером ⤵️</b>",
        parse_mode="HTML",
        reply_markup=get_manager_contact_keyboard(
            leave_phone_callback_data=leave_phone_callback_data,
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("auto_model:leave_phone:"))
async def auto_model_leave_phone_callback(callback: types.CallbackQuery, state: FSMContext):
    await ensure_user_exists(callback.from_user)
    parts = callback.data.split(":")
    if len(parts) not in (6, 7):
        await callback.answer(_get_auto_model_placeholder_text())
        return

    _, _, category_id, country_id, engine_id, model_id, *rest = parts
    source_token = rest[0] if rest else ""
    model_title = (
        _get_auto_model_lead_message(
            category_id,
            model_id,
            country_id=country_id,
            engine_id=engine_id,
        )
        or _get_auto_model_title(
            category_id,
            model_id,
            country_id=country_id,
            engine_id=engine_id,
        )
        or model_id
    )
    price_range_label = _build_auto_price_range_label(category_id, country_id, engine_id)

    await state.set_state(LeadStates.waiting_phone_country)
    await state.update_data(
        pending_lead_action="auto_model_leave_phone",
        pending_lead_message_text=model_title,
        pending_lead_price_range=price_range_label,
        pending_back_target="home",
        manual_phone_country=None,
        manual_phone_context={
            "category_id": category_id,
            "country_id": country_id,
            "engine_id": engine_id,
            "model_id": model_id,
            "source_token": source_token,
        },
    )
    await callback.message.answer(
        "🌍 Выберите страну номера, который хотите оставить:",
        reply_markup=get_phone_country_keyboard(
            back_callback_data=_get_auto_model_pick_callback_data(
                category_id,
                country_id,
                engine_id,
                model_id,
                source_token,
            ),
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("lead_phone_country:"))
async def lead_phone_country_callback(callback: types.CallbackQuery, state: FSMContext):
    await ensure_user_exists(callback.from_user)
    if await state.get_state() != LeadStates.waiting_phone_country.state:
        await callback.answer("Сценарий выбора номера уже неактуален.")
        return

    country_code = callback.data.split(":", maxsplit=1)[1]
    country_label_map = {
        "ru": "РФ",
        "by": "РБ",
    }
    country_label = country_label_map.get(country_code)
    if country_label is None:
        await callback.answer("Не удалось определить страну номера.")
        return

    await state.set_state(LeadStates.waiting_manual_phone)
    await state.update_data(
        manual_phone_country=country_code,
        manual_phone_country_label=country_label,
    )
    example = "+79991234567" if country_code == "ru" else "+375291234567"
    await callback.message.answer(
        f"📱 Введите номер {country_label} вручную.\nПример: {example}",
        reply_markup=get_manual_phone_request_keyboard(),
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
