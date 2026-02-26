from tgBot.bot.shared import *


@router.callback_query(F.data == "lead:auto_in_transit")
async def auto_in_transit_callback(callback: types.CallbackQuery, bot: Bot):
    await ensure_user_exists(callback.from_user)
    await callback.message.answer("Запрос по авто в пути принят.")
    await callback.answer()


@router.callback_query(F.data == "catalog:auto_in_path")
async def auto_in_path_catalog_callback(callback: types.CallbackQuery, bot: Bot):
    await ensure_user_exists(callback.from_user)
    await callback.answer()

    source_channel_id = await get_auto_in_path_channel_id()
    if source_channel_id is None:
        await callback.message.answer(
            "Канал/группа «Авто в пути» не настроен. Администратор должен указать ID канала в админке."
        )
        return

    sent_batches = await send_auto_in_transit_posts_to_user(bot, callback.from_user.id)
    if sent_batches > 0:
        return
    await callback.message.answer(
        "Скоро появятся новые лоты, и вы сразу получите уведомление."
    )
    return


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
        "Ниже тебя ждут подборки реальных авто в любой бюджет с живыми отзывами наших клиентов.\n\n"
        "💯Autopartner— это когда авто из США перестаёт быть просто идеей. С чего начнём?",
        reply_markup=get_start_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data == "info:quick_main")
async def quick_main_info_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    await callback.message.answer(
        "🔍 Всё, что вы хотели спросить — собрано тут. Нажимай на\n"
        "любой вопрос ниже 👇",
        reply_markup=get_quick_main_keyboard(),
    )
    await callback.answer()


@router.callback_query(F.data.startswith("quick_main:"))
async def quick_main_topic_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    topic_id = callback.data.split(":", maxsplit=1)[1]
    if topic_id == "delivery":
        await callback.message.answer(
            "🌍 Путь из Штатов: сколько едет авто?\n\n"
            "🛳️В среднем — 2–4 месяца. Бывает быстрее, бывает чуть\n"
            "дольше. Зависит от порта, погоды и настроения Вселенной.\n\n"
            "Мы не крутим штурвал, но всегда держим вас в курсе. И да —\n"
            "даём трек-номер, как на Алике :)\n\n"
            "👇 Ниже по кнопке — несколько отзывов наших клиентов:\n"
            "кто-то получил авто за 2,5 месяца, кому-то пришлось ждать\n"
            "подольше. Мы не скрываем — реальные кейсы бывают\n"
            "разные, и мы об этом честно говорим.",
            reply_markup=get_quick_main_delivery_keyboard(),
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
            reply_markup=get_quick_main_credit_keyboard(),
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
            reply_markup=get_quick_main_credit_keyboard(),
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
            reply_markup=get_quick_main_credit_keyboard(),
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
        "auction": "Покупка авто на аукционе",
        "delivery": "Сколько едет авто из США?",
        "credit": "Кредит/лизинг",
        "insurance": "Авто страхуется?",
        "hidden_damage": "Скрытые повреждения",
    }
    title = topic_titles.get(topic_id, topic_id)
    await callback.message.answer(
        f"Раздел «{title}» добавлю следующим шагом.",
        reply_markup=get_quick_main_keyboard(),
    )
    await callback.answer()


