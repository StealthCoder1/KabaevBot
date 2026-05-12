from tgBot.bot.shared import *
from tgBot.keyboards import get_lead_saved_keyboard


def _extract_phone_input(message: types.Message) -> str:
    contact = getattr(message, "contact", None)
    if contact and getattr(contact, "phone_number", None):
        return str(contact.phone_number).strip()
    return (message.text or message.caption or "").strip()


def _normalize_phone_for_country(text: str, country_code: str) -> str | None:
    digits = re.sub(r"\D", "", text)
    if country_code == "ru":
        if len(digits) == 11 and digits.startswith("8"):
            return f"+7{digits[1:]}"
        if len(digits) == 11 and digits.startswith("7"):
            return f"+{digits}"
        if len(digits) == 10:
            return f"+7{digits}"
        return None

    if country_code == "by":
        if len(digits) == 12 and digits.startswith("375"):
            return f"+{digits}"
        if len(digits) == 11 and digits.startswith("80"):
            return f"+375{digits[2:]}"
        if len(digits) == 10 and digits.startswith("0"):
            return f"+375{digits[1:]}"
        if len(digits) == 9:
            return f"+375{digits}"
        return None

    return None


def _phone_error_message(country_code: str, country_label: str, digits: str) -> str:
    if not digits:
        return (
            f"Не приняли номер {country_label}: в сообщении нет цифр.\n"
            f"Формат: {_manual_phone_example(country_code)}"
        )

    digit_count = len(digits)
    if country_code == "ru":
        if digit_count not in (10, 11):
            reason = f"некорректная длина ({digit_count} цифр)"
        elif digit_count == 11 and not (digits.startswith("7") or digits.startswith("8")):
            reason = "номер должен начинаться с 7 или 8"
        else:
            reason = "неверный формат номера"
        return (
            f"Не приняли номер РФ: {reason}.\n"
            f"Принимаем РФ в формате {_manual_phone_example('ru')} "
            f"(допустимо также начинать с 8)."
        )

    if country_code == "by":
        if digit_count not in (9, 10, 11, 12):
            reason = f"некорректная длина ({digit_count} цифр)"
        elif digit_count == 12 and not digits.startswith("375"):
            reason = "для 12 цифр номер должен начинаться с 375"
        elif digit_count == 11 and not digits.startswith("80"):
            reason = "для 11 цифр номер должен начинаться с 80"
        elif digit_count == 10 and not digits.startswith("0"):
            reason = "для 10 цифр номер должен начинаться с 0"
        else:
            reason = "неверный формат номера"
        return (
            f"Не приняли номер РБ: {reason}.\n"
            f"Принимаем РБ в формате {_manual_phone_example('by')} "
            f"(допустимо также: 80291234567 или 291234567)."
        )

    return (
        f"Не приняли номер: неизвестная страна '{country_label}'.\n"
        "Выберите страну и отправьте номер еще раз."
    )


def _manual_phone_example(country_code: str) -> str:
    return "+79991234567" if country_code == "ru" else "+375291234567"


async def _start_contact_flow(message: types.Message, state: FSMContext) -> None:
    await ensure_user_exists(message.from_user)
    await start_phone_country_flow(
        message,
        state,
        lead_action="contact_manager",
        back_target="home",
        back_callback_data="lead:contact_manager",
    )


async def _show_contact_manager_choices(message: types.Message) -> None:
    await message.answer(
        CONTACT_MANAGER_CHOICE_TEXT,
        parse_mode="HTML",
        reply_markup=get_manager_contact_keyboard(),
    )


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
    await state.clear()
    await _show_contact_manager_choices(callback.message)
    await callback.answer()


@router.callback_query(F.data == "lead:contact_manager:phone")
async def contact_manager_phone_callback(callback: types.CallbackQuery, state: FSMContext):
    await start_phone_country_flow(
        callback.message,
        state,
        lead_action="contact_manager",
        back_target="home",
        back_callback_data="lead:contact_manager"
    )
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

    await start_phone_country_flow(
        callback.message,
        state,
        lead_action="post_like",
        lead_message_text=lead_message_text,
        lead_price_range=lead_price_range,
        back_target="home",
        back_callback_data="guarantees:home",
    )
    await callback.answer()


@router.message(F.text == CONTACT_MANAGER_TEXT)
async def contact_manager_reply_button_handler(message: types.Message, state: FSMContext):
    await ensure_user_exists(message.from_user)
    await _show_contact_manager_choices(message)


@router.message(Command("manager"))
async def contact_manager_command_handler(message: types.Message, state: FSMContext):
    await ensure_user_exists(message.from_user)
    await state.clear()
    await _show_contact_manager_choices(message)


@router.message(LeadStates.waiting_phone_country)
async def waiting_phone_country_message(message: types.Message):
    await message.answer("Выберите страну номера кнопкой выше: РФ или РБ.")


@router.message(LeadStates.waiting_manual_phone)
async def collect_manual_phone(message: types.Message, state: FSMContext, bot: Bot):
    text = _extract_phone_input(message)
    state_data = await state.get_data()
    country_code = state_data.get("manual_phone_country")
    if not country_code:
        await message.answer("Сначала выберите страну номера: РФ или РБ.")
        return

    phone = _normalize_phone_for_country(text, country_code)
    if phone is None:
        digits = re.sub(r"\D", "", text)
        country_label = state_data.get("manual_phone_country_label") or country_code.upper()
        await message.answer(
            _phone_error_message(country_code, country_label, digits),
            reply_markup=types.ReplyKeyboardRemove(),
        )
        return

    try:
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

        await message.answer(
            # Always send confirmation to user, even if admin notification fails
            LEAD_SAVED_TEXT,
            parse_mode="HTML",
            reply_markup=get_lead_saved_keyboard(),
        )

        try:
            await notify_admins_new_lead(bot, lead)
        except Exception as notify_exc:
            logger.error(f"Ошибка уведомления админов (manual): {notify_exc}")

        await state.clear()
    except Exception as exc:
        logger.error(f"Критическая ошибка в collect_manual_phone: {exc}")
        # Always send confirmation to user, even if lead saving fails
        await message.answer(
            LEAD_SAVED_TEXT,
            parse_mode="HTML",
            reply_markup=get_lead_saved_keyboard(),
        )
        await state.clear()
