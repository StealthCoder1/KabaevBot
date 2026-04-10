from tgBot.bot.shared import *


async def _show_channel_menu(message: types.Message) -> None:
    await message.answer(
        "🔥 Актуальные варианты публикуем в канале. Нажмите кнопку ниже, чтобы открыть его.",
        reply_markup=get_quick_main_topic_keyboard(
            back_callback_data="guarantees:home",
            include_channel=True,
        ),
    )


async def _show_auto_in_path_intro(message: types.Message) -> None:
    await message.answer(
        "<b>Мы регулярно отслеживаем аукционы 🇺🇸 и отбираем наиболее выгодные варианты.</b>\n\n"
        "Все представленные ниже авто находятся в продаже и в ближайшее время будут доставлены в Беларусь.",
        parse_mode="HTML",
        reply_markup=get_auto_in_path_intro_keyboard(),
    )


async def _show_quick_main_menu(message: types.Message) -> None:
    await message.answer(
        "Выберите интересующий вопрос ⤵️",
        reply_markup=get_quick_main_keyboard(),
    )


@router.message(Command("channel"))
async def channel_command(message: types.Message, state: FSMContext):
    await ensure_user_exists(message.from_user)
    await state.clear()
    await _show_channel_menu(message)


@router.message(Command("in_path"))
async def auto_in_path_command(message: types.Message, state: FSMContext):
    await ensure_user_exists(message.from_user)
    await state.clear()
    await _show_auto_in_path_intro(message)


@router.message(Command("faq"))
async def quick_main_info_command(message: types.Message, state: FSMContext):
    await ensure_user_exists(message.from_user)
    await state.clear()
    await _show_quick_main_menu(message)


@router.callback_query(F.data == "lead:auto_in_transit")
async def auto_in_transit_callback(callback: types.CallbackQuery, bot: Bot):
    await ensure_user_exists(callback.from_user)
    await callback.message.answer("Запрос по авто в пути принят.")
    await callback.answer()


@router.callback_query(F.data == "catalog:auto_in_path")
async def auto_in_path_catalog_callback(callback: types.CallbackQuery, bot: Bot):
    await ensure_user_exists(callback.from_user)
    await _show_auto_in_path_intro(callback.message)
    await callback.answer()


@router.callback_query(F.data == "catalog:auto_in_path:show")
async def auto_in_path_catalog_show_callback(callback: types.CallbackQuery, bot: Bot):
    await ensure_user_exists(callback.from_user)
    await callback.answer()

    source_channel_id = await get_auto_in_path_channel_id()
    if source_channel_id is None:
        await callback.message.answer(
            "Канал/группа «Авто в пути» не настроен. Администратор должен указать ID канала в админке."
        )
        return

    sent_post = await send_auto_in_transit_post_to_user(bot, callback.from_user.id, batch_index=0)
    if sent_post:
        return
    await callback.message.answer(
        "Скоро появятся новые лоты, и вы сразу получите уведомление."
    )
    return


@router.callback_query(F.data.startswith("auto_in_path:next:"))
async def auto_in_path_next_callback(callback: types.CallbackQuery, bot: Bot):
    await ensure_user_exists(callback.from_user)

    parts = callback.data.split(":")
    if len(parts) != 3:
        await callback.answer("Не удалось открыть следующий пост.")
        return

    try:
        batch_index = int(parts[2])
    except ValueError:
        await callback.answer("Не удалось открыть следующий пост.")
        return

    sent_post = await send_auto_in_transit_post_to_user(bot, callback.from_user.id, batch_index=batch_index)
    if sent_post:
        await callback.answer()
        return

    await callback.answer("Больше постов пока нет.")


@router.callback_query(F.data == "info:guarantees")
async def guarantees_info_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    await callback.message.answer(
        "✅ Надёжность в деталях: наши гарантии\n\n"
        "📄 Договор не для галочки.\n"
        "Мы работаем как бизнес, а не как «дружеская услуга». У вас\n"
        "есть документ — и это главное.\n"
        "📊 Прозрачность до винтика.\n"
        "Мы не прячем нюансы. Лучше заранее всё обсудить, чем\n"
        "потом объяснять, «почему так вышло».\n"
        "📞 Вы в курсе даже мелочей.\n"
        "«Выкупили тачку», «вышла с порта», «стоит на СТО» — вы всё\n"
        "это знаете раньше, чем спросите.\n"
        "🏁 Визуальный контроль.\n"
        "Мы не просто пишем «машина пришла». Мы показываем. С\n"
        "фото, с видео, с реальными кадрами.\n"
        "🛡️ Деньги на виду.\n"
        "Никаких «откатов» и туманных оплат. Официальные\n"
        "переводы и полная отчётность.\n\n"
        "Мы за честность и спокойствие.\n"
        "Чтобы вы не волновались — а просто ждали свою тачку с\n"
        "кайфом.\n\n"
        "👉 Мы с вами до конца — сражаемся с бюрократией, решаем\n"
        "вопросы и поддерживаем на каждом шаге, ведь когда-то вы\n"
        "выбрали нас, и мы это ценим 🙌\n"
        "Но, как и в любых отношениях, взаимное уважение —\n"
        "ключевое. Никакой грубости и неуважения не терпим, потому\n"
        "что в Autopartner мы не только работаем с автомобилями, но и\n"
        "создаём атмосферу, где комфортно всем.",
        reply_markup=get_guarantees_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "guarantees:risks")
async def guarantees_risks_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    await callback.message.answer(
        "🚧 Риски? Знаем. Предупреждены. Готовы.\n\n"
        "Покупка на аукционе — это всегда немного риск.\n"
        "Но мы:\n"
        "✔️ выбираем авто и мото с минимальными повреждениями;\n"
        "✔️ проверяем историю (Carfax, AutoCheck);\n"
        "✔️ честно рассказываем обо всех нюансах;\n"
        "✔️ советуем по ремонту и стоимости запчастей.\n"
        "✔️ и — да! — каждый лот уже с базовой страховкой (можно\n"
        "добавить расширенную страховку, чтобы вообще без нервов)\n\n"
        "Вы всегда знаете, на что идёте.\n"
        "⚠️ Мы не скрываем риски (иногда всплывают мелкие тех или\n"
        "косметические нюансы, которых не было на фото), но\n"
        "минимизируем их по максимуму.",
        reply_markup=get_guarantees_risks_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "guarantees:home")
async def guarantees_home_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    await callback.message.answer(
        HOME_MENU_TEXT,
        reply_markup=get_start_keyboard(),
        parse_mode="HTML",
    )
    await callback.answer()


@router.callback_query(F.data == "info:quick_main")
async def quick_main_info_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    await _show_quick_main_menu(callback.message)
    await callback.answer()


@router.callback_query(F.data.startswith("quick_main:"))
async def quick_main_topic_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    topic_id = callback.data.split(":", maxsplit=1)[1]
    if topic_id == "equipment":
        await callback.message.answer(
            "🛻 Какую еще технику можно привезти?\n\n"
            "Сейчас в боте мы подбираем:\n"
            "🚗 автомобили из США, Китая и Кореи;\n"
            "🏍️ мотоциклы из США.\n\n"
            "Если вас интересует конкретная техника или редкая модель, напишите менеджеру — "
            "скажем честно, сможем ли привезти и какой нужен бюджет.",
            reply_markup=get_quick_main_topic_keyboard(include_manager=True),
        )
        await callback.answer()
        return

    if topic_id == "pricing":
        await callback.message.answer(
            "💵 Сколько стоят ваши услуги?\n\n"
            "Фиксированной цены для всех нет: итог зависит от выбранного авто или мото, "
            "страны покупки, стоимости лота, логистики, ремонта и формата сопровождения.\n\n"
            "Перед покупкой мы заранее считаем полный бюджет под ключ, чтобы вы понимали "
            "все расходы до принятия решения.",
            reply_markup=get_quick_main_topic_keyboard(include_manager=True),
        )
        await callback.answer()
        return

    if topic_id == "delivery":
        await callback.message.answer(
            "🛳️ Какие сроки доставки?\n\n"
            "В среднем доставка занимает 2–4 месяца.\n"
            "Срок зависит от страны отправления, порта, логистики и загрузки.\n\n"
            "На каждом этапе держим вас в курсе: выкуп, отправка, порт, СТО и выдача.",
            reply_markup=get_quick_main_topic_keyboard(include_manager=True),
        )
        await callback.answer()
        return

    if topic_id == "guarantees":
        await guarantees_info_callback(callback)
        return

    if topic_id == "location":
        await callback.message.answer(
            "📍 Где нас найти?\n\n"
            "Пишите нам в Telegram: @autopartner_import\n"
            "Актуальные варианты публикуем в канале: @autopartner_by\n\n"
            "Если хотите обсудить подбор, бюджет или конкретную модель, используйте кнопки ниже.",
            reply_markup=get_quick_main_topic_keyboard(include_manager=True, include_channel=True),
        )
        await callback.answer()
        return

    if topic_id == "credit":
        await callback.message.answer(
            "💳 А можно купить авто в кредит или лизинг?\n\n"
            "📉 Лизинг не прокатит.\n"
            "На авто с аукционов США оформить лизинг юридически\n"
            "нельзя (так что если вам где-то обещают «всё сделаем» —\n"
            "лучше пройти мимо этой компании).\n"
            "✔️ Кредит — возможно.\n"
            "Банковский потребительский. Если хочется машину уже\n"
            "сейчас — может быть решением, если не хватает до 30\n"
            "000BYN.\n\n"
            "✉️ Пишите — посоветуем варианты и поможем сделать всё\n"
            "правильно.",
            reply_markup=get_quick_main_credit_keyboard(auto_pick_source="quick_main_credit"),
        )
        await callback.answer()
        return

    if topic_id == "insurance":
        await callback.message.answer(
            "🛡️ Страховка: надо ли отдельно страховать авто при\n"
            "доставке?\n\n"
            "Нет, отдельно ничего оформлять не нужно — уже\n"
            "застраховано.\n"
            "Когда мы покупаем для вас авто на аукционе, оно\n"
            "автоматически попадает под страховое покрытие до\n"
            "прибытия в порт назначения — базовая защита от угона,\n"
            "утери или серьёзных повреждений в пути.\n"
            "👇 Есть вариант расширенной страховки, оплачивается\n"
            "отдельно и обычно актуален для машин стоимостью от 15k$.\n"
            "Это дополнительная защита для вашего спокойствия.\n\n"
            "Но помним: страховка не покрывает мелкие царапины или\n"
            "технику внутри салона, если что.\n\n"
            "✉️ Хотите спокойствия? Напишите — подберём авто и\n"
            "оформим всё грамотно.",
            reply_markup=get_quick_main_credit_keyboard(auto_pick_source="quick_main_insurance"),
        )
        await callback.answer()
        return

    if topic_id == "hidden_damage":
        await callback.message.answer(
            "🤔 А если всплывут скрытые повреждения?\n\n"
            "Такое бывает — это же аукцион, не салон. Мы проверяем\n"
            "машины по базам, но иногда вылезают мелкие тех. или\n"
            "косметические нюансы, которых не было на фото.\n\n"
            "Зато именно такие авто стоят дешевле. Чуть вложился — и\n"
            "катаешься на крутом варианте, который выгодно обошёлся.\n\n"
            "💡 Вопрос не в том, «а вдруг я потеряю?», а в том, «сколько я\n"
            "упускаю выгоды в денежном эквиваленте», если не\n"
            "воспользуюсь этим шансом.\n\n"
            "👇 Напишите менеджеру — всё объясним и начнём искать\n"
            "ваш вариант.",
            reply_markup=get_quick_main_credit_keyboard(auto_pick_source="quick_main_hidden_damage"),
        )
        await callback.answer()
        return

    if topic_id == "auction":
        await callback.message.answer(
            "🛒 Как проходит покупка авто с аукциона?\n\n"
            "✔️Обсуждаем, что вам нужно\n"
            "На старте — честный разговор: какие марки, пробег, тип\n"
            "кузова, допустимые повреждения. Лучше рассматривать 2–3\n"
            "модели, а не одну — это заметно расширяет выбор.\n"
            "✔️Отправляем подборки\n"
            "Раз в 2-3 дня шлём вам лоты с аукциона. Сначала — общий\n"
            "список, чтобы понять, что вам «заходит» визуально. Это\n"
            "помогает нам настроить прицел и давать точечные\n"
            "предложения.\n"
            "✔️Проверяем и считаем\n"
            "Если понравилось — проверяем историю, считаем стоимость\n"
            "доставки, ремонта, растаможки и прочих расходов.\n"
            "✔️Вы выбираете темп\n"
            "Можно найти за пару недель. Можно ждать 1–2 месяца ради\n"
            "«того самого» авто. Всё зависит от ваших приоритетов:\n"
            "быстрее и проще — или дольше, но топчик. Мы подстроимся.\n\n"
            "👉Мы здесь, чтобы весь путь — от первого лота до парковки\n"
            "под окном был для вас понятным, честным и реально\n"
            "выгодным.\n\n"
            "✉️Зачем тянуть? Пишите менеджеру. Он подскажет, с чего\n"
            "лучше начать и покажет самые сочные варианты для вас.",
            reply_markup=get_quick_main_auction_keyboard(),
        )
        await callback.answer()
        return

    topic_titles = {
        "equipment": "Какую еще технику можно привезти?",
        "pricing": "Сколько стоят ваши услуги?",
        "auction": "Покупка авто на аукционе",
        "delivery": "Какие сроки доставки?",
        "credit": "Кредит/лизинг",
        "insurance": "Авто страхуется?",
        "hidden_damage": "Скрытые повреждения",
        "guarantees": "Есть ли гарантии?",
        "location": "Где нас найти?",
    }
    title = topic_titles.get(topic_id, topic_id)
    await callback.message.answer(
        f"Раздел «{title}» добавлю следующим шагом.",
        reply_markup=get_quick_main_keyboard(),
    )
    await callback.answer()


