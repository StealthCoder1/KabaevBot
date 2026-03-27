import json
from pathlib import Path

from aiogram import types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from log import logger
from tgBot.texts import BACK_BUTTON_TEXT

MOTO_CATALOG_PATH = Path(__file__).resolve().parent.parent / "Data" / "json" / "moto_catalog.json"
_moto_catalog_cache = None
AUTO_CATALOG_PATH = Path(__file__).resolve().parent.parent / "Data" / "json" / "auto_catalog.json"
_auto_catalog_cache = None
MAX_PROFIT_LOTS_PATH = Path(__file__).resolve().parent.parent / "Data" / "json" / "max_profit_lots.json"
_max_profit_lots_cache = None

def _load_moto_catalog() -> dict:
    global _moto_catalog_cache
    if _moto_catalog_cache is not None:
        return _moto_catalog_cache

    try:
        _moto_catalog_cache = json.loads(MOTO_CATALOG_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.error(f"Не удалось загрузить moto_catalog.json: {exc}")
        _moto_catalog_cache = {}

    return _moto_catalog_cache

def _load_auto_catalog() -> dict:
    global _auto_catalog_cache
    if _auto_catalog_cache is not None:
        return _auto_catalog_cache

    try:
        _auto_catalog_cache = json.loads(AUTO_CATALOG_PATH.read_text(encoding="utf-8"))
    except Exception as exc:
        logger.error(f"Не удалось загрузить auto_catalog.json: {exc}")
        _auto_catalog_cache = {}

    return _auto_catalog_cache

def _load_max_profit_lots() -> list[dict]:
    global _max_profit_lots_cache
    if _max_profit_lots_cache is not None:
        return _max_profit_lots_cache

    try:
        data = json.loads(MAX_PROFIT_LOTS_PATH.read_text(encoding="utf-8"))
        if isinstance(data, list):
            _max_profit_lots_cache = [item for item in data if isinstance(item, dict)]
        else:
            _max_profit_lots_cache = []
    except Exception as exc:
        logger.error(f"Не удалось загрузить max_profit_lots.json: {exc}")
        _max_profit_lots_cache = []

    return _max_profit_lots_cache

def _get_max_profit_lots() -> tuple[dict[str, str], ...]:
    lots: list[dict[str, str]] = []
    for item in _load_max_profit_lots():
        lot_id = str(item.get("id", "")).strip()
        title = str(item.get("title", "")).strip()
        text = str(item.get("text", "")).strip()
        photo_path = str(item.get("photo_path", "")).strip()
        if not lot_id or not title or not text:
            continue
        lots.append(
            {
                "id": lot_id,
                "title": title,
                "text": text,
                "photo_path": photo_path,
            }
        )
    return tuple(lots)

def _auto_catalog_categories() -> list[dict]:
    data = _load_auto_catalog()
    categories = data.get("categories", []) if isinstance(data, dict) else []
    return [item for item in categories if isinstance(item, dict)]

def _get_auto_category_config(category_id: str) -> dict | None:
    for item in _auto_catalog_categories():
        if str(item.get("id", "")).strip() == category_id:
            return item
    return None

def _get_auto_category_label(category_id: str) -> str:
    category = _get_auto_category_config(category_id)
    if category:
        label = str(category.get("label", "")).strip()
        if label:
            return label

    fallback_labels = {
        "9_12k": "9 000$ - 12 000$",
        "12_15k": "12 000$ - 15 000$",
        "15_20k": "15 000$ - 20 000$",
        "20_30k": "20 000$ - 30 000$",
        "30k_plus_lux": "30 000$+ (люкс)",
        "electric": "Электрокары",
    }
    return fallback_labels.get(category_id, category_id)

def _extract_auto_models(container: dict | None) -> list[dict]:
    if not isinstance(container, dict):
        return []
    models = container.get("models", [])
    if not isinstance(models, list):
        return []
    return [item for item in models if isinstance(item, dict)]

def _get_auto_category_models(category_id: str) -> list[dict]:
    return _extract_auto_models(_get_auto_category_config(category_id))

def _get_auto_category_countries(category_id: str) -> list[dict]:
    category = _get_auto_category_config(category_id)
    if not category:
        return []
    countries = category.get("countries", [])
    if not isinstance(countries, list):
        return []
    return [item for item in countries if isinstance(item, dict)]

def _auto_category_has_countries(category_id: str) -> bool:
    return bool(_get_auto_category_countries(category_id))

def _get_auto_country_config(category_id: str, country_id: str) -> dict | None:
    for item in _get_auto_category_countries(category_id):
        if str(item.get("id", "")).strip() == country_id:
            return item
    return None

def _get_auto_country_title(category_id: str, country_id: str) -> str | None:
    country = _get_auto_country_config(category_id, country_id)
    if country:
        title = str(country.get("title", "")).strip()
        if title:
            return title

    fallback_titles = {
        "usa": "США",
        "china": "Китай",
        "korea": "Корея",
    }
    return fallback_titles.get(country_id)

def _get_auto_country_models(category_id: str, country_id: str) -> list[dict]:
    return _extract_auto_models(_get_auto_country_config(category_id, country_id))

def _resolve_keyboard_rows(layout: object, items_count: int) -> list[int]:
    rows: list[int] = []
    if isinstance(layout, list):
        for value in layout:
            if isinstance(value, int) and value > 0:
                rows.append(value)

    if rows:
        rows = rows.copy()
        total = sum(rows)
        if total < items_count:
            rows.extend([1] * (items_count - total))
        elif total > items_count:
            overflow = total - items_count
            while overflow > 0 and rows:
                idx = len(rows) - 1
                cut = min(rows[idx], overflow)
                rows[idx] -= cut
                overflow -= cut
                if rows[idx] == 0:
                    rows.pop()
        if not rows:
            rows = [1] * items_count
    else:
        rows = [1] * items_count
    return rows

def _append_source_token(callback_data: str, source_token: str = "") -> str:
    if not source_token:
        return callback_data
    return f"{callback_data}:{source_token}"

def _get_auto_countries_keyboard(
    category_id: str,
    back_callback_data: str = "lead:auto_pick",
    source_token: str = "",
) -> types.InlineKeyboardMarkup | None:
    countries = _get_auto_category_countries(category_id)
    if not countries:
        return None

    kb = InlineKeyboardBuilder()
    rows: list[int] = []
    items_count = 0
    for country in countries:
        country_id = str(country.get("id", "")).strip()
        title = str(country.get("title", "")).strip()
        if not country_id or not title:
            continue
        kb.button(
            text=title,
            callback_data=_append_source_token(
                f"price_country:{category_id}:{country_id}",
                source_token,
            ),
        )
        rows.append(1)
        items_count += 1

    if items_count == 0:
        return None

    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(*rows, 1)
    return kb.as_markup()

def _get_auto_models_keyboard(
    category_id: str,
    back_callback_data: str = "lead:auto_pick",
    country_id: str | None = None,
    source_token: str = "",
) -> types.InlineKeyboardMarkup | None:
    category = _get_auto_category_config(category_id)
    if not category:
        return None

    callback_prefix = ""
    callback_builder = None
    layout = category.get("layout", [])
    if country_id:
        country = _get_auto_country_config(category_id, country_id)
        if not country:
            return None
        models = _get_auto_country_models(category_id, country_id)
        layout = country.get("layout", [])
        callback_builder = lambda model_id: _append_source_token(
            f"auto_model_pick:{category_id}:{country_id}:{model_id}",
            source_token,
        )
    else:
        if _auto_category_has_countries(category_id):
            return None
        callback_prefix = str(category.get("callback_prefix", "")).strip()
        models = _get_auto_category_models(category_id)
        if callback_prefix:
            callback_builder = lambda model_id: f"{callback_prefix}:{model_id}"

    if callback_builder is None or not models:
        return None

    kb = InlineKeyboardBuilder()
    items_count = 0
    for model in models:
        model_id = str(model.get("id", "")).strip()
        title = str(model.get("title", "")).strip()
        if not model_id or not title:
            continue
        kb.button(text=title, callback_data=callback_builder(model_id))
        items_count += 1

    if items_count == 0:
        return None

    rows = _resolve_keyboard_rows(layout, items_count)

    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(*rows, 1)

    return kb.as_markup()

def _find_model_by_id(models: list[dict], model_id: str) -> dict | None:
    for model in models:
        if str(model.get("id", "")).strip() == model_id:
            return model
    return None

def _get_auto_model_country_id(category_id: str, model_id: str) -> str | None:
    for country in _get_auto_category_countries(category_id):
        country_id = str(country.get("id", "")).strip()
        if not country_id:
            continue
        if _find_model_by_id(_extract_auto_models(country), model_id):
            return country_id
    return None

def _get_auto_model_config(
    category_id: str,
    model_id: str,
    country_id: str | None = None,
) -> dict | None:
    if country_id:
        return _find_model_by_id(_get_auto_country_models(category_id, country_id), model_id)

    model = _find_model_by_id(_get_auto_category_models(category_id), model_id)
    if model:
        return model

    return _find_model_by_id(
        [
            model
            for country in _get_auto_category_countries(category_id)
            for model in _extract_auto_models(country)
        ],
        model_id,
    )

def _get_auto_model_title(
    category_id: str,
    model_id: str,
    country_id: str | None = None,
) -> str | None:
    model = _get_auto_model_config(category_id, model_id, country_id=country_id)
    if not model:
        return None
    title = str(model.get("title", "")).strip()
    return title or None

def _get_auto_model_lead_message(
    category_id: str,
    model_id: str,
    country_id: str | None = None,
) -> str | None:
    # lead_message in JSON is deprecated: always use model title
    return _get_auto_model_title(category_id, model_id, country_id=country_id)

def _get_auto_model_description_text(
    category_id: str,
    model_id: str,
    country_id: str | None = None,
) -> str:
    model = _get_auto_model_config(category_id, model_id, country_id=country_id)
    if not model:
        return _get_auto_model_placeholder_text()

    text = _join_catalog_lines(model.get("description_lines") or model.get("screen_lines"))
    if text.strip():
        return text

    title = _get_auto_model_title(category_id, model_id, country_id=country_id) or model_id
    return f"{title}\n\n{_get_auto_model_placeholder_text()}"

def _get_auto_model_photo_path(
    category_id: str,
    model_id: str,
    country_id: str | None = None,
) -> str | None:
    model = _get_auto_model_config(category_id, model_id, country_id=country_id)
    if not model:
        return None
    value = str(model.get("photo_path", "")).strip()
    return value or None

def _get_auto_model_placeholder_text() -> str:
    data = _load_auto_catalog()
    if isinstance(data, dict):
        value = data.get("model_click_placeholder")
        if isinstance(value, str) and value.strip():
            return value
    return "Подборка по модели авто будет добавлена следующим шагом"

def _moto_catalog_classes() -> list[dict]:
    data = _load_moto_catalog()
    classes = data.get("classes", []) if isinstance(data, dict) else []
    return [item for item in classes if isinstance(item, dict)]

def _get_moto_class_config(class_id: str) -> dict | None:
    for item in _moto_catalog_classes():
        if item.get("id") == class_id:
            return item
    return None

def _join_catalog_lines(lines: object) -> str:
    if isinstance(lines, str):
        return lines
    if isinstance(lines, list):
        return "\n".join(str(line) for line in lines)
    return ""

def _get_moto_intro_texts() -> tuple[str, str]:
    data = _load_moto_catalog()
    if not isinstance(data, dict):
        return "", ""
    intro = data.get("intro", {})
    if not isinstance(intro, dict):
        return "", ""
    title = _join_catalog_lines(intro.get("title_lines"))
    hint = _join_catalog_lines(intro.get("hint_lines"))
    return title, hint

def _get_moto_model_placeholder_text() -> str:
    data = _load_moto_catalog()
    if isinstance(data, dict):
        value = data.get("model_click_placeholder")
        if isinstance(value, str) and value.strip():
            return value
    return "Подборка по модели мото будет добавлена следующим шагом"

def _get_moto_models_keyboard(class_id: str) -> types.InlineKeyboardMarkup | None:
    class_cfg = _get_moto_class_config(class_id)
    if not class_cfg:
        return None

    models = class_cfg.get("models", [])
    if not isinstance(models, list) or not models:
        return None

    kb = InlineKeyboardBuilder()
    rows = []
    for model in models:
        if not isinstance(model, dict):
            continue
        model_id = str(model.get("id", "")).strip()
        title = str(model.get("title", "")).strip()
        if not model_id or not title:
            continue
        kb.button(text=title, callback_data=f"moto_model:{class_id}:{model_id}")
        rows.append(1)

    if not rows:
        return None

    kb.button(text=BACK_BUTTON_TEXT, callback_data="lead:moto_pick")
    rows.append(1)
    kb.adjust(*rows)
    return kb.as_markup()

def _get_moto_model_config(class_id: str, model_id: str) -> dict | None:
    class_cfg = _get_moto_class_config(class_id)
    if not class_cfg:
        return None
    models = class_cfg.get("models", [])
    if not isinstance(models, list):
        return None
    for model in models:
        if not isinstance(model, dict):
            continue
        if str(model.get("id", "")).strip() == model_id:
            return model
    return None

def _get_moto_model_title(class_id: str, model_id: str) -> str | None:
    model = _get_moto_model_config(class_id, model_id)
    if not model:
        return None
    title = str(model.get("title", "")).strip()
    return title or None

def _get_moto_model_lead_message(class_id: str, model_id: str) -> str | None:
    # lead_message in JSON is deprecated: always use model title
    return _get_moto_model_title(class_id, model_id)

def _get_moto_model_description_text(class_id: str, model_id: str) -> str:
    model = _get_moto_model_config(class_id, model_id)
    if not model:
        return _get_moto_model_placeholder_text()

    text = _join_catalog_lines(model.get("description_lines") or model.get("screen_lines"))
    if text.strip():
        return text

    title = _get_moto_model_title(class_id, model_id) or model_id
    return f"{title}\n\n{_get_moto_model_placeholder_text()}"

