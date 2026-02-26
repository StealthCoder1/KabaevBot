from tgBot.bot.shared import *


@router.callback_query(F.data == "lead:moto_pick")
async def moto_pick_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    title_text, hint_text = _get_moto_intro_texts()
    await callback.message.answer(
        title_text
        or "🏍️ Добро пожаловать в мото-бот Autopartner!\nПодберем для вас идеальный мотоцикл в нужном классе:",
        reply_markup=get_moto_classes_keyboard(),
    )
    if hint_text:
        await callback.message.answer(hint_text)
    else:
        await callback.message.answer(
            "💬 Выберите категорию, которая вам интересна, и мы найдем\n"
            "лучшие варианты!"
        )
    await callback.answer()


@router.callback_query(F.data.startswith("moto_class:"))
async def moto_class_callback(callback: types.CallbackQuery, bot: Bot):
    await ensure_user_exists(callback.from_user)
    payload = callback.data.split(":", maxsplit=1)[1]
    class_cfg = _get_moto_class_config(payload)
    label_map = {
        "sport": "Спорт",
        "street": "Стрит",
        "cruiser": "Крузер",
    }
    moto_class = (
        str(class_cfg.get("display_name", "")).strip()
        if class_cfg
        else label_map.get(payload, payload)
    )
    lead_message = (
        str(class_cfg.get("lead_message", "")).strip()
        if class_cfg
        else ""
    ) or f"Класс мото: {moto_class}"
    if class_cfg:
        screen_text = _join_catalog_lines(class_cfg.get("screen_lines"))
        models_markup = _get_moto_models_keyboard(payload)
        if screen_text and models_markup is not None:
            await callback.message.answer(screen_text, reply_markup=models_markup)
        elif screen_text:
            await callback.message.answer(screen_text)
        elif models_markup is not None:
            await callback.message.answer(
                f"Вы выбрали класс: {moto_class}.", reply_markup=models_markup
            )
        else:
            await callback.message.answer(
                f"Вы выбрали класс: {moto_class}.\n"
                "Категория готова к наполнению. Добавьте модели в JSON."
            )
        await callback.answer()
        return

    if payload == "sport":
        await callback.message.answer(
            "👇 Выбирайте модель — и смотрите, за сколько мы реально\n"
            "привозим такие мото нашим клиентам.\n"
            "P.S. цены ниже рынка РБ до 40%\n\n"
            "❕ Часто цена зависит от множества факторов, и даже одна и\n"
            "та же модель с одинаковым годом может стоить по-разному,\n"
            "потому что:\n"
            "➡️ Степень повреждений\n"
            "➡️ Пробег\n"
            "➡️ Комплектация\n\n"
            "Мы ориентируемся на статистику и реальные аукционные\n"
            "данные!\n\n"
            "Начнём? 👇",
            reply_markup=get_moto_sport_models_keyboard(),
        )
        await callback.answer()
        return

    if payload == "street":
        await callback.message.answer(
            "🔥 Лучшие стрит-мотоциклы в бюджете 5–30k$\n"
            "👇 Выбирайте модель — и смотрите, за сколько мы реально\n"
            "привозим такие мото нашим клиентам.\n"
            "P.S. цены ниже рынка РБ до 40%\n\n"
            "🏍️ Идеальны для города, путешествий и ежедневных поездок\n\n"
            "❕ Часто цена зависит от множества факторов, и даже одна и\n"
            "та же модель с одинаковым годом может стоить по-разному,\n"
            "потому что:\n"
            "➡️ Степень повреждений\n"
            "➡️ Пробег\n"
            "➡️ Комплектация\n\n"
            "Мы ориентируемся на статистику и реальные аукционные\n"
            "данные!\n\n"
            "Начнём? 👇",
            reply_markup=get_moto_street_models_keyboard(),
        )
        await callback.answer()
        return

    if payload == "cruiser":
        await callback.message.answer(
            "🔥 Лучшие крузеры в бюджете 10–15k$\n"
            "👇 Выбирайте модель — и смотрите, за сколько мы реально\n"
            "привозим такие мото нашим клиентам.\n"
            "P.S. цены ниже рынка РБ до 40%\n\n"
            "🏍️ Идеальны для размеренных поездок с максимальным\n"
            "комфортом и стильным классическим дизайном\n\n"
            "❕ Часто цена зависит от множества факторов, и даже одна и\n"
            "та же модель с одинаковым годом может стоить по-разному,\n"
            "потому что:\n"
            "➡️ Степень повреждений\n"
            "➡️ Пробег\n"
            "➡️ Комплектация\n\n"
            "Мы ориентируемся на статистику и реальные аукционные\n"
            "данные!\n"
            "Начнём? 👇",
            reply_markup=get_moto_cruiser_models_keyboard(),
        )
        await callback.answer()
        return

    await callback.message.answer(
        f"Вы выбрали класс: {moto_class}.\n"
        "Запрос принят, менеджер поможет с подбором."
    )
    await callback.answer()


@router.callback_query(F.data.startswith("moto_model:") & (~F.data.startswith("moto_model:want:")))
async def moto_model_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer(_get_moto_model_placeholder_text())
        return

    _, class_id, model_id = parts
    if not _get_moto_model_title(class_id, model_id):
        await callback.answer(_get_moto_model_placeholder_text())
        return

    await _show_moto_model_card(callback, class_id=class_id, model_id=model_id)
    await callback.answer()


@router.callback_query(F.data.startswith("moto_model:want:"))
async def moto_model_want_callback(callback: types.CallbackQuery, state: FSMContext):
    await ensure_user_exists(callback.from_user)
    parts = callback.data.split(":")
    if len(parts) != 5:
        await callback.answer("Не удалось определить модель мото.")
        return

    _, _, _, class_id, model_id = parts
    model_title = _get_moto_model_title(class_id, model_id)
    class_cfg = _get_moto_class_config(class_id)
    class_name = (
        str(class_cfg.get("display_name", "")).strip()
        if class_cfg
        else class_id
    )
    lead_message = _get_moto_model_lead_message(class_id, model_id) or model_title or model_id
    if not model_title:
        await callback.answer("Не удалось определить модель мото.")
        return

    await state.set_state(LeadStates.waiting_contact)
    await state.update_data(
        pending_lead_action="moto_model_want",
        pending_lead_message_text=f"{class_name}: {lead_message}",
        pending_lead_price_range=f"Мото / {class_name}",
    )
    await callback.message.answer(
        "🏍️ Отличный выбор. Отправьте номер, и подготовим подборку лотов по этому мото.\n\n"
        "Нажмите кнопку ниже 👇",
        reply_markup=get_contact_request_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("moto_sport:model:"))
async def moto_sport_model_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    model_id = _extract_model_id(callback.data)
    await _show_moto_model_card(callback, class_id="sport", model_id=model_id)
    await callback.answer()


@router.callback_query(F.data.startswith("moto_street:model:"))
async def moto_street_model_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    model_id = _extract_model_id(callback.data)
    await _show_moto_model_card(callback, class_id="street", model_id=model_id)
    await callback.answer()


@router.callback_query(F.data.startswith("moto_cruiser:model:"))
async def moto_cruiser_model_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    model_id = _extract_model_id(callback.data)
    await _show_moto_model_card(callback, class_id="cruiser", model_id=model_id)
    await callback.answer()


