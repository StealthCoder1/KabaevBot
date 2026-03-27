from aiogram import F, types
from aiogram.fsm.context import FSMContext

from tgBot.bot.shared import _show_moto_model_card, ensure_user_exists, router
from tgBot.catalogs import (
    _get_moto_class_config,
    _get_moto_intro_texts,
    _get_moto_model_lead_message,
    _get_moto_model_placeholder_text,
    _get_moto_model_title,
    _get_moto_models_keyboard,
    _join_catalog_lines,
)
from tgBot.keyboards import get_contact_request_keyboard, get_moto_classes_keyboard
from tgBot.states import LeadStates
from tgBot.texts import (
    MOTO_HINT_FALLBACK_TEXT,
    MOTO_INTRO_FALLBACK_TEXT,
    MOTO_MODEL_RESOLVE_ERROR_TEXT,
)

MOTO_BUDGET_LABELS = {
    "up_to_10k": "до 10k$",
    "10_20k": "10–20k$",
    "20k_plus": "20k$+",
}


@router.callback_query((F.data == "lead:moto_pick") | F.data.startswith("lead:moto_pick:"))
async def moto_pick_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    parts = callback.data.split(":", maxsplit=2)
    source = parts[2] if len(parts) == 3 else ""
    back_callback_data = {
        "risks": "guarantees:risks",
        "quick_main_delivery": "quick_main:delivery",
    }.get(source, "guarantees:home")
    title_text, hint_text = _get_moto_intro_texts()
    await callback.message.answer(
        title_text or MOTO_INTRO_FALLBACK_TEXT,
        reply_markup=get_moto_classes_keyboard(back_callback_data=back_callback_data),
    )
    await callback.message.answer(hint_text or MOTO_HINT_FALLBACK_TEXT)
    await callback.answer()


@router.callback_query(F.data.startswith("moto_class:"))
async def moto_class_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    budget_id = callback.data.split(":", maxsplit=1)[1]
    budget_cfg = _get_moto_class_config(budget_id)
    budget_name = (
        str(budget_cfg.get("display_name", "")).strip()
        if budget_cfg
        else MOTO_BUDGET_LABELS.get(budget_id, budget_id)
    )

    if budget_cfg:
        screen_text = _join_catalog_lines(budget_cfg.get("screen_lines"))
        models_markup = _get_moto_models_keyboard(budget_id)
        if screen_text and models_markup is not None:
            await callback.message.answer(screen_text, reply_markup=models_markup)
        elif screen_text:
            await callback.message.answer(screen_text)
        elif models_markup is not None:
            await callback.message.answer(
                f"Вы выбрали бюджет: {budget_name}.",
                reply_markup=models_markup,
            )
        else:
            await callback.message.answer(
                f"Вы выбрали бюджет: {budget_name}.\n"
                "Раздел готов к наполнению. Добавьте модели в JSON."
            )
        await callback.answer()
        return

    await callback.message.answer(
        f"Вы выбрали бюджет: {budget_name}.\n"
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

    _, budget_id, model_id = parts
    if not _get_moto_model_title(budget_id, model_id):
        await callback.answer(_get_moto_model_placeholder_text())
        return

    await _show_moto_model_card(callback, class_id=budget_id, model_id=model_id)
    await callback.answer()


@router.callback_query(F.data.startswith("moto_model:want:"))
async def moto_model_want_callback(callback: types.CallbackQuery, state: FSMContext):
    await ensure_user_exists(callback.from_user)
    parts = callback.data.split(":", maxsplit=3)
    if len(parts) != 4:
        await callback.answer(MOTO_MODEL_RESOLVE_ERROR_TEXT)
        return

    _, _, budget_id, model_id = parts
    model_title = _get_moto_model_title(budget_id, model_id)
    budget_cfg = _get_moto_class_config(budget_id)
    budget_name = (
        str(budget_cfg.get("display_name", "")).strip()
        if budget_cfg
        else MOTO_BUDGET_LABELS.get(budget_id, budget_id)
    )
    lead_message = _get_moto_model_lead_message(budget_id, model_id) or model_title or model_id
    if not model_title:
        await callback.answer(MOTO_MODEL_RESOLVE_ERROR_TEXT)
        return

    await state.set_state(LeadStates.waiting_contact)
    await state.update_data(
        pending_lead_action="moto_model_want",
        pending_lead_message_text=f"{budget_name}: {lead_message}",
        pending_lead_price_range=f"Мото / {budget_name}",
        pending_back_target="moto_pick",
    )
    await callback.message.answer(
        "🏍️ Отличный выбор. Отправьте номер, и подготовим подборку лотов по этому мото.\n\n"
        "Нажмите кнопку ниже 👇",
        reply_markup=get_contact_request_keyboard(),
    )
    await callback.answer()
