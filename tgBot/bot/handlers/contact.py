from tgBot.bot.shared import *


def _default_reply_keyboard_for_user(user: types.User | None):
    if user and is_admin(user.id):
        return get_admin_keyboard()
    return types.ReplyKeyboardRemove()

def _manual_phone_example(country_code: str) -> str:
    return "+79991234567" if country_code == "ru" else "+375291234567"

def _normalize_phone_for_country(text: str, country_code: str) -> str | None:
    digits = re.sub(r"\D", "", text)
    if country_code == "ru":
        if len(digits) == 11 and digits.startswith("8"):
            return f"+7{digits[1:]}"
        if len(digits) == 11 and digits.startswith("7"):
            return f"+{digits}"
        return None

    if country_code == "by":
        if len(digits) == 12 and digits.startswith("375"):
            return f"+{digits}"
        if len(digits) == 11 and digits.startswith("80"):
            return f"+375{digits[2:]}"
        return None

    return None


async def _start_contact_flow(message: types.Message, state: FSMContext) -> None:
    await ensure_user_exists(message.from_user)
    await state.set_state(LeadStates.waiting_contact)
    await state.update_data(
        pending_lead_action="contact_manager",
        pending_lead_message_text=None,
        pending_lead_price_range=None,
        pending_back_target="home",
    )
    await message.answer(LEAD_CONTACT_REQUEST_TEXT, reply_markup=get_contact_request_keyboard())


async def _show_back_target_menu(message: types.Message, back_target: str) -> None:
    if back_target == "auto_pick":
        await message.answer(
            BUDGET_PROMPT_TEXT,
            parse_mode="HTML",
            reply_markup=get_price_range_keyboard(),
        )
        return

    if back_target == "moto_pick":
        title_text, hint_text = _get_moto_intro_texts()
        await message.answer(
            title_text
            or hint_text
            or MOTO_INTRO_FALLBACK_TEXT,
            reply_markup=get_moto_classes_keyboard(),
        )
        return

    await message.answer(
        HOME_MENU_TEXT,
        reply_markup=get_start_keyboard(),
        parse_mode="HTML",
    )


def _message_plain_text(message: types.Message | None) -> str:
    if message is None:
        return ""
    return (message.text or message.caption or "").strip()


def _build_post_like_lead_text(
    message: types.Message | None,
    source_chat_id: int,
    source_message_id: int,
) -> str:
    candidates = [
        _message_plain_text(getattr(message, "reply_to_message", None)),
        _message_plain_text(message),
    ]
    for candidate in candidates:
        if not candidate or candidate in {
            POST_LIKE_PROMPT_TEXT,
            AUTO_IN_PATH_BROWSER_PROMPT_TEXT,
        }:
            continue

        normalized_text = re.sub(r"\s+", " ", candidate).strip()
        if normalized_text:
            return f"{normalized_text[:160]} [post {source_chat_id}:{source_message_id}]"

    return f"Пост из группы [post {source_chat_id}:{source_message_id}]"


@router.callback_query(F.data == "lead:contact_manager")
async def contact_manager_callback(callback: types.CallbackQuery, state: FSMContext):
    await ensure_user_exists(callback.from_user)
    await callback.message.answer(
        CONTACT_MANAGER_CHOICE_TEXT,
        parse_mode="HTML",
        reply_markup=get_manager_contact_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "lead:contact_manager:phone")
async def contact_manager_phone_callback(callback: types.CallbackQuery, state: FSMContext):
    await _start_contact_flow(callback.message, state)
    await callback.answer()


@router.callback_query(F.data.startswith("post_like:"))
async def post_like_callback(callback: types.CallbackQuery, state: FSMContext):
    await ensure_user_exists(callback.from_user)

    parts = callback.data.split(":", maxsplit=2)
    if len(parts) != 3:
        await callback.answer("Не удалось определить пост.")
        return

    try:
        source_chat_id = int(parts[1])
        source_message_id = int(parts[2])
    except ValueError:
        await callback.answer("Не удалось определить пост.")
        return

    auto_in_path_channel_id = await get_auto_in_path_channel_id()
    lead_price_range = "Авто в пути" if source_chat_id == auto_in_path_channel_id else "Пост из группы"
    lead_message_text = _build_post_like_lead_text(
        callback.message,
        source_chat_id,
        source_message_id,
    )

    await state.set_state(LeadStates.waiting_contact)
    await state.update_data(
        pending_lead_action="post_like",
        pending_lead_message_text=lead_message_text,
        pending_lead_price_range=lead_price_range,
        pending_back_target="home",
    )
    await callback.message.answer(
        LEAD_CONTACT_REQUEST_TEXT,
        reply_markup=get_contact_request_keyboard(),
    )
    await callback.answer()


@router.message(F.text == CONTACT_MANAGER_TEXT)
async def contact_manager_reply_button_handler(message: types.Message, state: FSMContext):
    await ensure_user_exists(message.from_user)
    await message.answer(
        CONTACT_MANAGER_CHOICE_TEXT,
        parse_mode="HTML",
        reply_markup=get_manager_contact_keyboard(),
    )


@router.message(LeadStates.waiting_contact, F.contact)
async def collect_contact_from_button(message: types.Message, state: FSMContext, bot: Bot):
    contact = message.contact
    if contact is None or not contact.phone_number:
        await message.answer(
            "Не удалось получить номер. Нажмите кнопку ниже ещё раз.",
            reply_markup=get_contact_request_keyboard(),
        )
        return

    customer_name = " ".join(
        part for part in [contact.first_name, contact.last_name] if part
    ).strip() or (message.from_user.full_name if message.from_user else "")

    phone = contact.phone_number.strip()
    await ensure_user_exists(message.from_user)

    state_data = await state.get_data()
    lead_action = state_data.get("pending_lead_action") or "contact_manager"
    lead_message_text = state_data.get("pending_lead_message_text") or "contact_button"
    lead_price_range = state_data.get("pending_lead_price_range")

    lead = await save_lead(
        from_user=message.from_user,
        action=lead_action,
        phone=phone,
        customer_name=customer_name or None,
        price_range=lead_price_range,
        message_text=lead_message_text,
    )
    await notify_admins_new_lead(bot, lead)
    await state.clear()
    await message.answer(
        LEAD_SAVED_TEXT,
        reply_markup=_default_reply_keyboard_for_user(message.from_user),
    )


@router.message(LeadStates.waiting_contact, F.text == BACK_BUTTON_TEXT)
@router.message(LeadStates.waiting_contact, F.text == "Назад")
async def contact_waiting_back_handler(message: types.Message, state: FSMContext):
    state_data = await state.get_data()
    back_target = state_data.get("pending_back_target") or "home"
    await state.clear()
    await _show_back_target_menu(message, back_target)


@router.message(LeadStates.waiting_contact)
async def collect_contact(message: types.Message, state: FSMContext, bot: Bot):
    text = (message.text or "").strip()
    match = re.search(r"(\+?\d[\d\-\s\(\)]{7,}\d)", text)
    phone = match.group(1).replace(" ", "") if match else None
    name = re.sub(r"(\+?\d[\d\-\s\(\)]{7,}\d)", "", text).strip(" ,.-")

    if phone and not name:
        name = (message.from_user.full_name if message.from_user else "").strip()

    if not phone:
        await message.answer(
            "Не удалось распознать номер.\n"
            "Отправьте номер в формате +79991234567\n"
            "или сообщением вида: Иван +79991234567."
        )
        return

    await ensure_user_exists(message.from_user)

    state_data = await state.get_data()
    lead_action = state_data.get("pending_lead_action") or "contact_manager"
    lead_message_text = state_data.get("pending_lead_message_text") or text
    lead_price_range = state_data.get("pending_lead_price_range")

    lead = await save_lead(
        from_user=message.from_user,
        action=lead_action,
        phone=phone,
        customer_name=name,
        price_range=lead_price_range,
        message_text=lead_message_text,
    )
    await notify_admins_new_lead(bot, lead)
    await state.clear()
    await message.answer(
        LEAD_SAVED_TEXT,
        reply_markup=_default_reply_keyboard_for_user(message.from_user),
    )


@router.message(LeadStates.waiting_phone_country)
async def waiting_phone_country_message(message: types.Message):
    await message.answer("Выберите страну номера кнопкой выше: РФ или РБ.")


@router.message(LeadStates.waiting_manual_phone)
async def collect_manual_phone(message: types.Message, state: FSMContext, bot: Bot):
    text = (message.text or "").strip()
    state_data = await state.get_data()
    country_code = state_data.get("manual_phone_country")
    if not country_code:
        await message.answer("Сначала выберите страну номера: РФ или РБ.")
        return

    phone = _normalize_phone_for_country(text, country_code)
    if phone is None:
        example = _manual_phone_example(country_code)
        country_label = state_data.get("manual_phone_country_label") or country_code.upper()
        await message.answer(
            f"Не удалось распознать номер {country_label}.\n"
            f"Отправьте его в формате {example}.",
            reply_markup=get_manual_phone_request_keyboard(),
        )
        return

    await ensure_user_exists(message.from_user)

    lead_action = state_data.get("pending_lead_action") or "auto_model_leave_phone"
    lead_message_text = state_data.get("pending_lead_message_text") or text
    lead_price_range = state_data.get("pending_lead_price_range")
    customer_name = (message.from_user.full_name if message.from_user else "").strip() or None

    lead = await save_lead(
        from_user=message.from_user,
        action=lead_action,
        phone=phone,
        customer_name=customer_name,
        price_range=lead_price_range,
        message_text=lead_message_text,
    )
    await notify_admins_new_lead(bot, lead)
    await state.clear()
    await message.answer(
        LEAD_SAVED_TEXT,
        reply_markup=_default_reply_keyboard_for_user(message.from_user),
    )
