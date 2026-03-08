from tgBot.bot.shared import *


def _default_reply_keyboard_for_user(user: types.User | None):
    if user and is_admin(user.id):
        return get_admin_keyboard()
    return get_user_reply_keyboard()


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
            reply_markup=get_price_range_keyboard(),
        )
        return

    if back_target == "moto_pick":
        title_text, hint_text = _get_moto_intro_texts()
        await message.answer(
            title_text
            or MOTO_INTRO_FALLBACK_TEXT,
            reply_markup=get_moto_classes_keyboard(),
        )
        if hint_text:
            await message.answer(hint_text)
        return

    if back_target == "best_deals":
        await message.answer(BEST_DEALS_NEXT_STEP_TEXT, reply_markup=get_best_deals_keyboard())
        return

    await message.answer(MAIN_MENU_ACTION_TEXT, reply_markup=get_start_keyboard())
    if not is_admin(message.from_user.id):
        await message.answer(MAIN_MENU_VARIANT_TEXT, reply_markup=get_user_reply_keyboard())


@router.callback_query(F.data == "lead:contact_manager")
async def contact_manager_callback(callback: types.CallbackQuery, state: FSMContext):
    await _start_contact_flow(callback.message, state)
    await callback.answer()


@router.message(F.text == CONTACT_MANAGER_TEXT)
async def contact_manager_reply_button_handler(message: types.Message, state: FSMContext):
    await _start_contact_flow(message, state)


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

    if not phone or not name:
        await message.answer(
            "Не удалось распознать данные. Формат: Имя +79991234567\n"
            "Или нажмите кнопку «📱 Отправить номер».",
            reply_markup=get_contact_request_keyboard(),
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
