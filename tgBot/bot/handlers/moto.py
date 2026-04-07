from aiogram import F, types
from aiogram.fsm.context import FSMContext

from tgBot.bot.shared import _show_moto_model_card, ensure_user_exists, router
from tgBot.catalogs import (
    _get_moto_class_config,
    _get_moto_class_display_name,
    _get_moto_model_lead_message,
    _get_moto_model_placeholder_text,
    _get_moto_model_title,
    _get_moto_models_keyboard,
)
from tgBot.keyboards import (
    get_contact_request_keyboard,
    get_moto_classes_keyboard,
    get_moto_country_keyboard,
)
from tgBot.states import LeadStates
from tgBot.texts import (
    MOTO_MODEL_RESOLVE_ERROR_TEXT,
)

MOTO_COUNTRY_ID = "usa"
MOTO_COUNTRY_TITLE = "США"
MOTO_BUDGET_PROMPT_TEXT = "<b>💸 В каком бюджете ищете мотоцикл?</b>"
MOTO_MODELS_BODY = (
    "Перед вами список, который подходят под заданные параметры.\n"
    "Важно: цена на одинаковые модели и годы выпуска может существенно различаться. "
    "Это зависит от нескольких ключевых факторов:\n"
    "•  степень повреждения,\n"
    "•  пробег,\n"
    "•  комплектация."
)
MOTO_MODELS_FOOTER = "Мы опираемся только на статистику, а значит — на реальные цифры, а не на догадки!"


def _get_moto_budget_intro_text(
    budget_name: str,
    country_title: str,
) -> str:
    return "\n".join(
        [
            f"Бюджет: <b>{budget_name}</b>",
            f"Страна: <b>{country_title}</b>",
            MOTO_MODELS_BODY,
            f"<b>{MOTO_MODELS_FOOTER}</b>",
        ]
    )


@router.callback_query((F.data == "lead:moto_pick") | F.data.startswith("lead:moto_pick:"))
async def moto_pick_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    parts = callback.data.split(":", maxsplit=2)
    source = parts[2] if len(parts) == 3 else ""
    back_callback_data = {
        "risks": "guarantees:risks",
        "quick_main_delivery": "quick_main:delivery",
    }.get(source, "guarantees:home")
    await callback.message.answer(
        MOTO_BUDGET_PROMPT_TEXT,
        parse_mode="HTML",
        reply_markup=get_moto_classes_keyboard(back_callback_data=back_callback_data),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("moto_class:"))
async def moto_class_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    budget_id = callback.data.split(":", maxsplit=1)[1]

    await callback.message.answer(
        "<b>Из какой страны рассматриваете мотоцикл?</b>",
        parse_mode="HTML",
        reply_markup=get_moto_country_keyboard(
            budget_id,
            back_callback_data="lead:moto_pick",
        ),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("moto_country:"))
async def moto_country_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer(MOTO_MODEL_RESOLVE_ERROR_TEXT)
        return

    _, budget_id, country_id = parts
    budget_name = _get_moto_class_display_name(budget_id) or budget_id
    country_title = MOTO_COUNTRY_TITLE if country_id == MOTO_COUNTRY_ID else country_id

    models_markup = _get_moto_models_keyboard(
        budget_id,
        back_callback_data=f"moto_class:{budget_id}",
    )
    if models_markup is not None:
        await callback.message.answer(
            _get_moto_budget_intro_text(budget_name, country_title),
            parse_mode="HTML",
            reply_markup=models_markup,
        )
        await callback.answer()
        return

    await callback.message.answer(
        f"Вы выбрали бюджет: {budget_name} / {country_title}.\n"
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
    budget_name = _get_moto_class_display_name(budget_id) or budget_id
    lead_message = _get_moto_model_lead_message(budget_id, model_id) or model_title or model_id
    if not model_title:
        await callback.answer(MOTO_MODEL_RESOLVE_ERROR_TEXT)
        return

    await state.set_state(LeadStates.waiting_contact)
    await state.update_data(
        pending_lead_action="moto_model_want",
        pending_lead_message_text=f"{budget_name} / {MOTO_COUNTRY_TITLE}: {lead_message}",
        pending_lead_price_range=f"Мото / {budget_name} / {MOTO_COUNTRY_TITLE}",
        pending_back_target="moto_pick",
    )
    await callback.message.answer(
        "🏍️ Отличный выбор. Отправьте номер, и подготовим подборку лотов по этому мото.\n\n"
        "Нажмите кнопку ниже 👇",
        reply_markup=get_contact_request_keyboard(),
    )
    await callback.answer()
