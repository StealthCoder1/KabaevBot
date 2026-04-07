import copy
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
AUTO_COUNTRY_DISPLAY_TITLES = {
    "usa": "США",
    "china": "Китай",
    "korea": "Корея",
}
AUTO_COUNTRY_BUTTON_ORDER = {
    "korea": 0,
    "china": 1,
    "usa": 2,
}
AUTO_ENGINE_BUTTON_PREFIXES = {
    "gasoline": "⛽️",
    "diesel": "⛽️",
    "electric": "⚡️",
}
AUTO_ENGINE_BUTTON_ORDER = {
    "gasoline": 0,
    "diesel": 1,
    "electric": 2,
}
AUTO_MODEL_SOURCE_OVERRIDES = {
    ("10_15k", "gasoline"): ("30k_plus", "usa", "gasoline"),
}
AUTO_MODEL_TITLE_OVERRIDES = {
    ("10_15k", "gasoline", "range_rover_velar"): "Land Rover Range Rover Velar",
}
MOTO_MODEL_OVERRIDES = {
    "5_10k": (
        {"model_id": "cbr1000rr_2008", "title": "Honda CBR1000RR"},
        {"model_id": "mt09", "title": "Yamaha MT-09"},
        {"model_id": "z900_2017", "title": "Kawasaki Z900"},
    ),
}


def _format_budget_label(label: str) -> str:
    return label.replace(" - ", " – ").strip()


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
            return _format_budget_label(label)

    fallback_labels = {
        "10_15k": "10 000$ - 16 000$",
        "15_20k": "16 000$ - 20 000$",
        "20_30k": "20 000$ - 30 000$",
        "30k_plus": "30 000$+",
    }
    return _format_budget_label(fallback_labels.get(category_id, category_id))


def _extract_auto_models(container: dict | None) -> list[dict]:
    if not isinstance(container, dict):
        return []
    models = container.get("models", [])
    if not isinstance(models, list):
        return []
    return [item for item in models if isinstance(item, dict)]


def _extract_auto_engines(container: dict | None) -> list[dict]:
    if not isinstance(container, dict):
        return []
    engines = container.get("engines", [])
    if not isinstance(engines, list):
        return []
    return [item for item in engines if isinstance(item, dict)]


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
            return AUTO_COUNTRY_DISPLAY_TITLES.get(country_id, title)

    return AUTO_COUNTRY_DISPLAY_TITLES.get(country_id)


def _get_country_flag(country_id: str) -> str:
    return {
        "usa": "🇺🇸",
        "china": "🇨🇳",
        "korea": "🇰🇷",
        "japan": "🇯🇵",
    }.get(country_id, "")


def _get_auto_country_engines(category_id: str, country_id: str) -> list[dict]:
    return _extract_auto_engines(_get_auto_country_config(category_id, country_id))


def _get_auto_engine_config(
    category_id: str,
    country_id: str,
    engine_id: str,
) -> dict | None:
    for item in _get_auto_country_engines(category_id, country_id):
        if str(item.get("id", "")).strip() == engine_id:
            return item
    return None


def _get_auto_engine_title(
    category_id: str,
    country_id: str,
    engine_id: str,
) -> str | None:
    engine = _get_auto_engine_config(category_id, country_id, engine_id)
    if engine:
        title = str(engine.get("title", "")).strip()
        if title:
            return title

    fallback_titles = {
        "gasoline": "Бензин",
        "diesel": "Дизель",
        "electric": "Электро",
    }
    return fallback_titles.get(engine_id)


def _get_auto_engine_button_text(
    category_id: str,
    country_id: str,
    engine_id: str,
) -> str:
    title = _get_auto_engine_title(category_id, country_id, engine_id) or engine_id
    prefix = AUTO_ENGINE_BUTTON_PREFIXES.get(engine_id, "")
    return f"{prefix} {title}".strip()


def _get_auto_model_override_source(
    category_id: str,
    country_id: str,
    engine_id: str,
) -> tuple[str, str, str] | None:
    override = AUTO_MODEL_SOURCE_OVERRIDES.get((category_id, engine_id))
    if not override:
        return None

    source_category_id, source_country_id, source_engine_id = override
    resolved_country_id = country_id if source_country_id == "*" else source_country_id
    return source_category_id, resolved_country_id, source_engine_id


def _apply_auto_model_title_overrides(
    category_id: str,
    engine_id: str,
    models: list[dict],
) -> list[dict]:
    overridden_models: list[dict] = []
    for model in models:
        model_copy = copy.deepcopy(model)
        model_id = str(model_copy.get("id", "")).strip()
        title_override = AUTO_MODEL_TITLE_OVERRIDES.get((category_id, engine_id, model_id))
        if title_override:
            model_copy["title"] = title_override
        overridden_models.append(model_copy)
    return overridden_models


def _get_auto_engine_models(
    category_id: str,
    country_id: str,
    engine_id: str,
) -> list[dict]:
    override_source = _get_auto_model_override_source(category_id, country_id, engine_id)
    if override_source is not None:
        source_category_id, source_country_id, source_engine_id = override_source
        source_models = _extract_auto_models(
            _get_auto_engine_config(source_category_id, source_country_id, source_engine_id)
        )
        return _apply_auto_model_title_overrides(category_id, engine_id, source_models)

    return _extract_auto_models(_get_auto_engine_config(category_id, country_id, engine_id))


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
    sorted_countries = sorted(
        countries,
        key=lambda country: (
            AUTO_COUNTRY_BUTTON_ORDER.get(str(country.get("id", "")).strip(), 99),
            str(country.get("title", "")).strip(),
        ),
    )
    for country in sorted_countries:
        country_id = str(country.get("id", "")).strip()
        title = _get_auto_country_title(category_id, country_id) or str(country.get("title", "")).strip()
        if not country_id or not title:
            continue
        country_flag = _get_country_flag(country_id)
        button_text = f"{country_flag} {title}".strip()
        kb.button(
            text=button_text,
            callback_data=_append_source_token(
                f"price_country:{category_id}:{country_id}",
                source_token,
            ),
        )
        rows.append(1)

    if not rows:
        return None

    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(*rows, 1)
    return kb.as_markup()


def _get_auto_engines_keyboard(
    category_id: str,
    country_id: str,
    back_callback_data: str = "lead:auto_pick",
    source_token: str = "",
) -> types.InlineKeyboardMarkup | None:
    country = _get_auto_country_config(category_id, country_id)
    if not country:
        return None

    engines = _get_auto_country_engines(category_id, country_id)
    if not engines:
        return None

    kb = InlineKeyboardBuilder()
    rows: list[int] = []
    sorted_engines = sorted(
        engines,
        key=lambda engine: (
            AUTO_ENGINE_BUTTON_ORDER.get(str(engine.get("id", "")).strip(), 99),
            str(engine.get("title", "")).strip(),
        ),
    )
    for engine in sorted_engines:
        engine_id = str(engine.get("id", "")).strip()
        title = _get_auto_engine_button_text(category_id, country_id, engine_id)
        if not engine_id or not title:
            continue
        kb.button(
            text=title,
            callback_data=_append_source_token(
                f"price_engine:{category_id}:{country_id}:{engine_id}",
                source_token,
            ),
        )
        rows.append(1)

    if not rows:
        return None

    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    kb.adjust(*rows, 1)
    return kb.as_markup()


def _get_auto_models_keyboard(
    category_id: str,
    back_callback_data: str = "lead:auto_pick",
    country_id: str | None = None,
    engine_id: str | None = None,
    source_token: str = "",
) -> types.InlineKeyboardMarkup | None:
    category = _get_auto_category_config(category_id)
    if not category or not country_id or not engine_id:
        return None

    country = _get_auto_country_config(category_id, country_id)
    if not country:
        return None

    engine = _get_auto_engine_config(category_id, country_id, engine_id)
    if not engine:
        return None

    models = _get_auto_engine_models(category_id, country_id, engine_id)
    if not models:
        return None

    layout = engine.get("layout", country.get("layout", category.get("layout", [])))

    kb = InlineKeyboardBuilder()
    items_count = 0
    for model in models:
        model_id = str(model.get("id", "")).strip()
        title = str(model.get("title", "")).strip()
        if not model_id or not title:
            continue
        kb.button(
            text=title,
            callback_data=_append_source_token(
                f"auto_model_pick:{category_id}:{country_id}:{engine_id}:{model_id}",
                source_token,
            ),
        )
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
            return copy.deepcopy(model)
    return None


def _get_auto_model_country_id(category_id: str, model_id: str) -> str | None:
    for country in _get_auto_category_countries(category_id):
        country_id = str(country.get("id", "")).strip()
        if not country_id:
            continue
        for engine in _get_auto_country_engines(category_id, country_id):
            if _find_model_by_id(_extract_auto_models(engine), model_id):
                return country_id
    return None


def _get_auto_model_engine_id(
    category_id: str,
    country_id: str,
    model_id: str,
) -> str | None:
    for engine in _get_auto_country_engines(category_id, country_id):
        engine_id = str(engine.get("id", "")).strip()
        if not engine_id:
            continue
        if _find_model_by_id(_extract_auto_models(engine), model_id):
            return engine_id
    return None


def _get_auto_model_config(
    category_id: str,
    model_id: str,
    country_id: str | None = None,
    engine_id: str | None = None,
) -> dict | None:
    if country_id and engine_id:
        return _find_model_by_id(
            _get_auto_engine_models(category_id, country_id, engine_id),
            model_id,
        )

    if country_id:
        for engine in _get_auto_country_engines(category_id, country_id):
            model = _find_model_by_id(_extract_auto_models(engine), model_id)
            if model:
                return model

    for country in _get_auto_category_countries(category_id):
        current_country_id = str(country.get("id", "")).strip()
        if not current_country_id:
            continue
        for engine in _get_auto_country_engines(category_id, current_country_id):
            model = _find_model_by_id(_extract_auto_models(engine), model_id)
            if model:
                return model
    return None


def _get_auto_model_title(
    category_id: str,
    model_id: str,
    country_id: str | None = None,
    engine_id: str | None = None,
) -> str | None:
    model = _get_auto_model_config(
        category_id,
        model_id,
        country_id=country_id,
        engine_id=engine_id,
    )
    if not model:
        return None
    title = str(model.get("title", "")).strip()
    return title or None


def _get_auto_model_lead_message(
    category_id: str,
    model_id: str,
    country_id: str | None = None,
    engine_id: str | None = None,
) -> str | None:
    return _get_auto_model_title(
        category_id,
        model_id,
        country_id=country_id,
        engine_id=engine_id,
    )


def _get_auto_model_description_text(
    category_id: str,
    model_id: str,
    country_id: str | None = None,
    engine_id: str | None = None,
) -> str:
    model = _get_auto_model_config(
        category_id,
        model_id,
        country_id=country_id,
        engine_id=engine_id,
    )
    if not model:
        return _get_auto_model_placeholder_text()

    text = _join_catalog_lines(model.get("description_lines") or model.get("screen_lines"))
    if text.strip():
        return text

    title = _get_auto_model_title(
        category_id,
        model_id,
        country_id=country_id,
        engine_id=engine_id,
    ) or model_id
    return f"{title}\n\n{_get_auto_model_placeholder_text()}"


def _get_auto_model_photo_path(
    category_id: str,
    model_id: str,
    country_id: str | None = None,
    engine_id: str | None = None,
) -> str | None:
    model = _get_auto_model_config(
        category_id,
        model_id,
        country_id=country_id,
        engine_id=engine_id,
    )
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


def _get_moto_class_display_name(class_id: str) -> str | None:
    class_cfg = _get_moto_class_config(class_id)
    if not class_cfg:
        return None

    display_name = str(class_cfg.get("display_name", "")).strip()
    if display_name:
        return _format_budget_label(display_name)

    button_text = str(class_cfg.get("button_text", "")).strip()
    if button_text:
        return _format_budget_label(button_text.lstrip("👉").strip())

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


def _get_moto_class_models(class_id: str) -> list[dict]:
    class_cfg = _get_moto_class_config(class_id)
    if not class_cfg:
        return []

    models = class_cfg.get("models", [])
    if not isinstance(models, list):
        return []

    prepared_models = [item for item in models if isinstance(item, dict)]
    override_specs = MOTO_MODEL_OVERRIDES.get(class_id)
    if not override_specs:
        return prepared_models

    models_by_id = {
        str(model.get("id", "")).strip(): model
        for model in prepared_models
    }
    overridden_models: list[dict] = []
    for spec in override_specs:
        model_id = str(spec.get("model_id", "")).strip()
        source_model = models_by_id.get(model_id)
        if not source_model:
            continue
        model_copy = copy.deepcopy(source_model)
        title_override = str(spec.get("title", "")).strip()
        if title_override:
            model_copy["title"] = title_override
        overridden_models.append(model_copy)

    return overridden_models


def _get_moto_models_keyboard(
    class_id: str,
    back_callback_data: str = "lead:moto_pick",
) -> types.InlineKeyboardMarkup | None:
    models = _get_moto_class_models(class_id)
    if not models:
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

    kb.button(text=BACK_BUTTON_TEXT, callback_data=back_callback_data)
    rows.append(1)
    kb.adjust(*rows)
    return kb.as_markup()


def _get_moto_model_config(class_id: str, model_id: str) -> dict | None:
    for model in _get_moto_class_models(class_id):
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
