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
    )
    await message.answer(
        "🚀 Введите номер — и стартуем с подбором\n\n"
        "Просто нажмите кнопку 👇",
        reply_markup=get_contact_request_keyboard(),
    )


@router.callback_query(F.data == "lead:contact_manager")
async def contact_manager_callback(callback: types.CallbackQuery, state: FSMContext):
    await _start_contact_flow(callback.message, state)
    await callback.answer()


@router.message(F.text == "Связаться с менеджером")
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
        "Спасибо. Менеджер свяжется с вами.",
        reply_markup=_default_reply_keyboard_for_user(message.from_user),
    )


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
        "Спасибо. Менеджер свяжется с вами.",
        reply_markup=_default_reply_keyboard_for_user(message.from_user),
    )
