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


async def _show_auto_in_path_finished(message: types.Message) -> None:
    await message.answer(
        "🏁 К сожалению, на данный момент это все автомобили, которые находятся в пути.\n"
        "При появлении новых выкупленных автомобилей мы незамедлительно вас уведомим.",
        reply_markup=get_auto_in_path_finished_keyboard(),
    )


async def _show_quick_main_menu(message: types.Message) -> None:
    await message.answer(
        "Выберите интересующий вопрос ⤵️",
        reply_markup=get_quick_main_keyboard(),
    )


PRICING_PACKAGE_TEXTS = {
    ("auto", "start"): (
        "Вы выбрали пакет «СТАРТ» 💻\n"
        "Этот пакет подходит для тех, кто занимается поиском автомобиля на аукционе самостоятельно "
        "и присылает варианты для проверки. Пакет включает:\n\n"
        "• Полное изучение вами выбранных автомобилей\n"
        "• Изучение истории обслуживания и ДТП (Carfax)\n"
        "• Торги выбранными авто по вашей ставке (неограниченное количество лотов)\n"
        "• Сопровождение юридически правильной сделки\n"
        "• Доставка авто до РБ (все города)\n"
        "• Страхование авто от США до РБ\n"
        "• Бесплатные Carfax\n"
        "• Сопровождение сделки фото/видео отчетами\n"
        "• Дистанционное оформление авто на СВХ (за доп. плату)\n"
        "• Дистанционное оформление ЭПТС (за доп. плату)\n"
        "• Подбор запчастей (за доп. плату)\n\n"
        "💳 Стоимость: 590 BYN"
    ),
    ("auto", "standard"): (
        "Вы выбрали пакет «СТАНДАРТ»\n"
        "Этот пакет подходит тем, кто занимается восстановлением автомобиля самостоятельно либо "
        "выбрал автомобиль без повреждений. Пакет включает:\n\n"
        "• Подбор автомобилей по вашим параметрам (без ограничений по количеству)\n"
        "• Полное изучение вами выбранных авто\n"
        "• Изучение истории обслуживания и ДТП (Carfax)\n"
        "• Предварительный расчет ставки в США\n"
        "• Просчёт итоговой стоимости авто в РБ\n"
        "• Просчёт стоимости ремонта авто\n"
        "• Торги выбранным авто по вашей ставке (неограниченное количество лотов)\n"
        "• Сопровождение юридически правильной сделки\n"
        "• Доставка авто до РБ (все города)\n"
        "• Страхование от США до РБ\n"
        "• Дистанционное оформление авто на СВХ (за доп. плату)\n"
        "• Дистанционное оформление ЭПТС (за доп. плату)\n"
        "• Бесплатные Carfax\n"
        "• Сопровождение сделки фото/видео отчетами\n\n"
        "💳 Стоимость: 990 BYN"
    ),
    ("auto", "key"): (
        "Вы выбрали пакет «ПОД КЛЮЧ»\n"
        "Этот пакет подходит тем, кто не хочет заморачиваться над выбором запчастей и ремонтом. "
        "Мы все сделаем самостоятельно на нашем сервисе и выдадим готовый автомобиль. Пакет включает:\n\n"
        "• Подбор автомобилей по вашим параметрам (без ограничений по количеству)\n"
        "• Полное изучение вами выбранных авто\n"
        "• Изучение истории обслуживания и ДТП (Carfax)\n"
        "• Предварительный расчёт ставки в США\n"
        "• Просчет итоговой стоимости авто в РБ\n"
        "• Просчет стоимости ремонта авто\n"
        "• Торги выбранным авто по вашей ставке (неограниченное количество лотов)\n"
        "• Сопровождение юридически правильной сделки\n"
        "• Доставка авто до РБ (все города)\n"
        "• Страхование от США до РБ\n"
        "• Дистанционное оформление авто на СВХ\n"
        "• Дистанционное оформление ЭПТС\n"
        "• Бесплатные Carfax\n"
        "• Сопровождение сделки фото/видео отчетами\n"
        "• Подбор автозапчастей и полное восстановление авто\n"
        "• Проведение ТО, а также доп. работ по автомобилю\n\n"
        "💳 Стоимость: 1890 BYN"
    ),
    ("moto", "start"): (
        "Вы выбрали пакет «СТАРТ» 💻\n"
        "Этот пакет подходит для тех, кто занимается поиском транспорта на аукционе самостоятельно "
        "и присылает варианты для проверки. Пакет включает:\n\n"
        "• Полное изучение вами выбранного транспорта\n"
        "• Изучение истории обслуживания и ДТП (Carfax)\n"
        "• Торги выбранного транспорта по вашей ставке (неограниченное количество лотов)\n"
        "• Сопровождение юридически правильной сделки\n"
        "• Доставка транспорта до РБ (все города)\n"
        "• Страхование транспорта от США до РБ\n"
        "• Бесплатные Carfax\n"
        "• Сопровождение сделки фото/видео отчетами\n"
        "• Дистанционное оформление транспорта на СВХ (за доп. плату)\n"
        "• Дистанционное оформление ЭПТС (за доп. плату)\n"
        "• Подбор запчастей (за доп. плату)\n\n"
        "💳 Стоимость: 490 BYN"
    ),
    ("moto", "standard"): (
        "Вы выбрали пакет «СТАНДАРТ»\n"
        "Этот пакет подходит тем, кто занимается восстановлением транспорта самостоятельно либо "
        "выбрал транспорт без повреждений. Пакет включает:\n\n"
        "• Подбор транспорта по вашим параметрам (без ограничений по количеству)\n"
        "• Полное изучение вами выбранного транспорта\n"
        "• Изучение истории обслуживания и ДТП (Carfax)\n"
        "• Предварительный расчет ставки в США\n"
        "• Просчет итоговой стоимости транспорта в РБ\n"
        "• Просчет стоимости ремонта транспорта\n"
        "• Торги выбранного транспорта по вашей ставке (неограниченное количество лотов)\n"
        "• Сопровождение юридически правильной сделки\n"
        "• Доставка транспорта до РБ (все города)\n"
        "• Страхование от США до РБ\n"
        "• Дистанционное оформление транспорта на СВХ (за доп. плату)\n"
        "• Дистанционное оформление ЭПТС (за доп. плату)\n"
        "• Бесплатные Carfax\n"
        "• Сопровождение сделки фото/видео отчетами\n\n"
        "💳 Стоимость: 690 BYN"
    ),
    ("moto", "key"): (
        "Вы выбрали пакет «ПОД КЛЮЧ»\n"
        "Этот пакет подходит тем, кто не хочет заморачиваться над выбором запчастей и ремонтом. "
        "Мы все сделаем самостоятельно на нашем сервисе и выдадим готовое транспортное средство. "
        "Пакет включает:\n\n"
        "• Подбор транспорта по вашим параметрам (без ограничений по количеству)\n"
        "• Полное изучение вами выбранного транспорта\n"
        "• Изучение истории обслуживания и ДТП (Carfax)\n"
        "• Предварительный расчёт ставки в США\n"
        "• Просчет итоговой стоимости транспорта в РБ\n"
        "• Просчет стоимости ремонта транспорта\n"
        "• Торги выбранного транспорта по вашей ставке (неограниченное количество лотов)\n"
        "• Сопровождение юридически правильной сделки\n"
        "• Доставка транспорта до РБ (все города)\n"
        "• Страхование от США до РБ\n"
        "• Дистанционное оформление транспорта на СВХ\n"
        "• Дистанционное оформление ЭПТС\n"
        "• Бесплатные Carfax\n"
        "• Сопровождение сделки фото/видео отчетами\n"
        "• Подбор запчастей и полное восстановление транспорта\n"
        "• Проведение ТО, а также доп. работ\n\n"
        "💳 Стоимость: по запросу BYN"
    ),
    ("kr_auto", "standard"): (
        "Пакет «СТАНДАРТ» 🚘\n"
        "Мы доставляем автомобили из Кореи и сопровождаем сделку полностью. Пакет включает:\n\n"
        "• Поиск и изучение автомобилей по вашим параметрам\n"
        "• Изучение истории обслуживания и ДТП вами выбранных авто\n"
        "• Выездной осмотр авто (фото + видео отчет прилагается)\n"
        "• Просчет итоговой стоимости авто в РБ\n"
        "• Бронирование авто за счет организации\n"
        "• Выкуп и доставка авто до территории РБ (все города)\n"
        "• Сопровождение юридически правильной сделки\n"
        "• Страхование авто на всем пути следования\n"
        "• Дистанционное оформление авто на СВХ (за доп. плату)\n"
        "• Дистанционное оформление ЭПТС (за доп. плату)\n"
        "• Сопровождение сделки фото/видео отчетами\n"
        "• Во всех авто лежат трекеры для отслеживания местоположения\n\n"
        "💳 Стоимость: 1090 BYN"
    ),
    ("kr_moto", "standard"): (
        "Пакет «СТАНДАРТ» 🚘\n"
        "Мы доставляем мото-, гидро- и квадроциклы из Кореи и сопровождаем сделку полностью. "
        "Данный пакет включает:\n\n"
        "• Подбор транспорта по вашим параметрам (без ограничений по количеству)\n"
        "• Полное изучение вами выбранного транспорта\n"
        "• Изучение истории обслуживания и ДТП\n"
        "• Просчет итоговой стоимости транспорта в РБ\n"
        "• Бронирование транспорта за счет организации\n"
        "• Выкуп и доставка транспорта до территории РБ (все города)\n"
        "• Сопровождение юридически правильной сделки\n"
        "• Страхование транспорта на всем пути следования\n"
        "• Дистанционное оформление ТС на СВХ (за доп. плату)\n"
        "• Дистанционное оформление ЭПТС (за доп. плату)\n"
        "• Сопровождение сделки фото/видео отчетами\n"
        "• В каждом транспорте находятся трекеры для отслеживания местоположения\n\n"
        "💳 Стоимость: 690 BYN"
    ),
    ("cn_auto", "standard"): (
        "Пакет «СТАНДАРТ» 🚘\n"
        "Мы доставляем автомобили из Китая и сопровождаем сделку полностью. Данный пакет включает:\n\n"
        "• Поиск и изучение авто по вашим параметрам\n"
        "• Изучение истории обслуживания и ДТП вами выбранных авто\n"
        "• Выездной осмотр (фото + видео отчет прилагается) за доп. плату\n"
        "• Просчет итоговой стоимости авто в РБ\n"
        "• Бронирование авто за счет организации\n"
        "• Выкуп и доставка авто до территории РБ (все города)\n"
        "• Сопровождение юридически правильной сделки\n"
        "• Страхование авто на всем пути следования\n"
        "• Дистанционное оформление авто на СВХ (за доп. плату)\n"
        "• Дистанционное оформление ЭПТС (за доп. плату)\n"
        "• Сопровождение сделки фото/видео отчетами\n\n"
        "💳 Стоимость: 1090 BYN"
    ),
}


async def _show_pricing_countries(message: types.Message) -> None:
    await message.answer(
        "Выберите страну, из которой хотите доставить технику:",
        reply_markup=get_pricing_countries_keyboard(),
    )


async def _show_pricing_usa_tech(message: types.Message) -> None:
    await message.answer(
        "Какую технику хотите привезти?",
        reply_markup=get_pricing_usa_tech_keyboard(),
    )


async def _show_pricing_korea_tech(message: types.Message) -> None:
    await message.answer(
        "Какую технику хотите привезти?",
        reply_markup=get_pricing_korea_tech_keyboard(),
    )


async def _show_pricing_packages(message: types.Message, tech: str) -> None:
    await message.answer(
        "По данному направлению у нас есть 3 пакета услуг:",
        reply_markup=get_pricing_packages_keyboard(tech),
    )


async def _show_pricing_package_detail(
    message: types.Message,
    package_text: str,
    *,
    tech: str,
    back_callback_data: str | None = None,
) -> None:
    await message.answer(
        package_text,
        reply_markup=get_pricing_package_detail_keyboard(
            tech,
            back_callback_data=back_callback_data,
        ),
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
    await _show_auto_in_path_finished(callback.message)
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
        if parts[2] == "none":
            await _show_auto_in_path_finished(callback.message)
            await callback.answer()
            return
        await callback.answer("Не удалось открыть следующий пост.")
        return

    sent_post = await send_auto_in_transit_post_to_user(bot, callback.from_user.id, batch_index=batch_index)
    if sent_post:
        await callback.answer()
        return

    await _show_auto_in_path_finished(callback.message)
    await callback.answer()


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


@router.callback_query(F.data.startswith("pricing:"))
async def pricing_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    parts = callback.data.split(":")

    if parts[:2] == ["pricing", "country"] and len(parts) == 3:
        country = parts[2]
        if country == "us":
            await _show_pricing_usa_tech(callback.message)
            await callback.answer()
            return

        if country == "kr":
            await _show_pricing_korea_tech(callback.message)
            await callback.answer()
            return

        if country == "cn":
            package_text = PRICING_PACKAGE_TEXTS[("cn_auto", "standard")]
            await _show_pricing_package_detail(
                callback.message,
                package_text,
                tech="auto",
                back_callback_data="quick_main:pricing",
            )
            await callback.answer()
            return

    if parts[:2] == ["pricing", "tech"] and len(parts) == 4:
        country = parts[2]
        tech = parts[3]
        if country == "us" and tech in {"auto", "moto"}:
            await _show_pricing_packages(callback.message, tech)
            await callback.answer()
            return

        if country == "kr" and tech in {"auto", "moto"}:
            package_text = PRICING_PACKAGE_TEXTS[(f"kr_{tech}", "standard")]
            await _show_pricing_package_detail(
                callback.message,
                package_text,
                tech=tech,
                back_callback_data="pricing:country:kr",
            )
            await callback.answer()
            return

        await callback.answer("Не удалось открыть пакеты услуг.")
        return

    if parts[:2] == ["pricing", "pkg"] and len(parts) == 5:
        country = parts[2]
        tech = parts[3]
        package = parts[4]
        package_text = PRICING_PACKAGE_TEXTS.get((tech, package))
        if country == "us" and package_text:
            await _show_pricing_package_detail(
                callback.message,
                package_text,
                tech=tech,
            )
            await callback.answer()
            return

        await callback.answer("Не удалось открыть пакет услуг.")
        return

    await callback.answer("Не удалось открыть раздел стоимости.")


@router.callback_query(F.data.startswith("quick_main:"))
async def quick_main_topic_callback(callback: types.CallbackQuery):
    await ensure_user_exists(callback.from_user)
    topic_id = callback.data.split(":", maxsplit=1)[1]
    if topic_id == "equipment":
        await callback.message.answer(
            "Мы осуществляем поставку техники из Южной Кореи, Китая, США и сопровождаем на всем пути следования 🗺\n\n"
            "📍 Китай\n"
            "Из Китая мы привозим автомобили.\n\n"
            "📍 Южная Корея\n"
            "Из Кореи мы доставляем автомобили, мотоциклы, гидроциклы и квадроциклы.\n\n"
            "📍 США\n"
            "Из США мы везем автомобили, мотоциклы, снегоходы, гидроциклы, квадроциклы и багги.\n\n"
            "Хотите узнать все подробности? Оставьте заявку ниже ⤵️",
            reply_markup=get_quick_main_request_keyboard(),
        )
        await callback.answer()
        return

    if topic_id == "pricing":
        await _show_pricing_countries(callback.message)
        await callback.answer()
        return

    if topic_id == "delivery":
        await callback.message.answer(
            "Какие сроки доставки?\n\n"
            "Средние сроки доставки автомобиля в Беларусь ⤵️\n\n"
            "🇺🇸 Из США (через Грузию): 3–4 месяца\n"
            "🇺🇸 Из США (через Литву): 2–3 месяца\n\n"
            "🇨🇳 Из Китая: 45–60 дней\n\n"
            "🇰🇷 Из Кореи: 60–90 дней\n\n"
            "*Указанные сроки являются ориентировочными и отражают среднюю логистику при штатном режиме перевозок.\n\n"
            "Сроки могут отличаться в зависимости от:\n\n"
            "• типа и габаритов транспорта\n"
            "• загруженности портов и погодных условий\n"
            "• очередей на границах и изменений таможенного законодательства\n"
            "• выбранного типа доставки",
            reply_markup=get_quick_main_back_keyboard(),
        )
        await callback.answer()
        return

    if topic_id == "guarantees":
        await callback.message.answer(
            "🤝 Мы предоставляем гарантии, которые защищают вас на каждом этапе сделки:\n\n"
            "• Страховка автомобиля на всем пути следования — от покупки до момента передачи вам.\n"
            "• Юридическая чистота — машина не в залоге, не под арестом, с прозрачной историей. Мы несем полную ответственность за документы.\n"
            "• Фиксированная стоимость сделки — вы знаете итоговую цену до старта. Никаких скрытых платежей.\n\n"
            "Почему нам доверяют?\n"
            "• Мы не первый год привозим авто из Кореи, Китая и США.\n"
            "• У нас есть магазин автозапчастей AUTOPARTNER с более чем 15-летней историей.\n"
            "• Большое количество реальных отзывов.\n"
            "• Мы на связи 24/7 — вы всегда знаете, где находится ваш автомобиль.\n\n"
            "⭐️ Наши отзывы\n"
            '<a href="https://yandex.by/maps/org/avtopartner_ekspress/161630834635/?ll=27.651950%2C53.931573&amp;utm_source=share&amp;z=16">Яндекс.Карты (Минск)</a> | '
            '<a href="https://yandex.by/maps/155/gomel/?ll=31.003815%2C52.429567&amp;mode=poi&amp;poi%5Bpoint%5D=31.003555%2C52.429490&amp;poi%5Buri%5D=ymapsbm1%3A%2F%2Forg%3Foid%3D80521825409&amp;utm_source=share&amp;z=19.22">Яндекс.Карты (Гомель)</a>',
            parse_mode="HTML",
            reply_markup=get_quick_main_back_keyboard(),
        )
        await callback.answer()
        return

    if topic_id == "location":
        await callback.message.answer(
            "Мы на связи в соцсетях и всегда рады видеть вас в наших офисах 🤝\n\n"
            "📱 Социальные сети\n"
            '<a href="http://t.me/autopartner_by">Telegram</a> | '
            '<a href="https://www.instagram.com/autopartner.by/">Instagram</a> | '
            '<a href="https://www.tiktok.com/@autopartner.by">TikTok</a> | '
            '<a href="https://www.youtube.com/@autopartner_group">YouTube</a> | '
            '<a href="https://cars.autopartner.by/">Наш сайт</a>\n\n'
            "📍 Адреса офисов\n"
            "г. Минск, ул. Петра Мстиславца, 18\n"
            "г. Гомель, ул. Жарковского, 22\n\n"
            "⭐️ Наши отзывы\n"
            '<a href="https://yandex.by/maps/org/avtopartner_ekspress/161630834635/?ll=27.651950%2C53.931573&amp;utm_source=share&amp;z=16">Яндекс.Карты (Минск)</a> | '
            '<a href="https://yandex.by/maps/155/gomel/?ll=31.003815%2C52.429567&amp;mode=poi&amp;poi%5Bpoint%5D=31.003555%2C52.429490&amp;poi%5Buri%5D=ymapsbm1%3A%2F%2Forg%3Foid%3D80521825409&amp;utm_source=share&amp;z=19.22">Яндекс.Карты (Гомель)</a>',
            parse_mode="HTML",
            reply_markup=get_quick_main_back_keyboard(),
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


