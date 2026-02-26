from tgBot.bot.shared import *
from tgBot.states import AdminStates
from aiogram.filters import StateFilter
import os


@router.message(CommandStart())
async def cmd_start(message: types.Message):
    await ensure_user_exists(message.from_user)
    await message.answer(
        "Ниже тебя ждут подборки реальных авто в любой бюджет с живыми отзывами наших клиентов.\n\n"
        "💯Autopartner— это когда авто из США перестаёт быть просто идеей. С чего начнём?",
        reply_markup=get_start_keyboard(),
    )
    if not is_admin(message.from_user.id):
        # Send a second message to apply the reply keyboard for regular users.
        await message.answer(
            "\u0412\u044b\u0431\u0435\u0440\u0438\u0442\u0435 \u0432\u0430\u0440\u0438\u0430\u043d\u0442",
            reply_markup=get_user_reply_keyboard(),
        )


@router.message(Command("admin"))
async def cmd_admin(message: types.Message):
    if not is_admin(message.from_user.id):
        await message.answer("Доступ запрещен.")
        return
    role = get_admin_role(message.from_user.id) or "admin"
    await message.answer(
        f"Админ-панель включена. Роль: {role}.",
        reply_markup=get_admin_keyboard(),
    )


async def count_users(session, start_date, end_date=None):
    # users.date_start is stored as naive UTC datetime in DB
    start_dt = datetime(start_date.year, start_date.month, start_date.day)
    if end_date is None:
        q = select(User).where(User.date_start >= start_dt)
    else:
        end_dt = datetime(end_date.year, end_date.month, end_date.day)
        q = select(User).where(
            User.date_start >= start_dt,
            User.date_start < end_dt,
        )
    result = await session.execute(q)
    return len(result.scalars().all())


async def send_stats(message: types.Message):
    async with async_session() as session:
        utcnow = datetime.utcnow()
        today = utcnow.date()
        a_week_ago = today - timedelta(days=7)
        a_month_ago = today - timedelta(days=30)
        a_year_ago = today - timedelta(days=365)
        counts = {
            "\u0421\u0435\u0433\u043e\u0434\u043d\u044f": await count_users(session, today),
            "\u041d\u0435\u0434\u0435\u043b\u044f": await count_users(session, a_week_ago),
            "\u041c\u0435\u0441\u044f\u0446": await count_users(session, a_month_ago),
            "\u0413\u043e\u0434": await count_users(session, a_year_ago),
        }

    msg = "\u0421\u0442\u0430\u0442\u0438\u0441\u0442\u0438\u043a\u0430 \u043f\u043e\u043b\u044c\u0437\u043e\u0432\u0430\u0442\u0435\u043b\u0435\u0439:\n" + "\n".join(
        [f"{k}: {v}" for k, v in counts.items()]
    )
    await message.answer(msg)


async def _send_stats_visual(message: types.Message) -> None:
    sticker_id = os.getenv("ADMIN_STATS_STICKER_ID", "").strip()
    if sticker_id:
        try:
            await message.answer_sticker(sticker_id)
            return
        except Exception as exc:
            logger.warning(f"Не удалось отправить стикер статистики: {exc}")

    # Fallback, если file_id ещё не настроен
    try:
        await message.answer_dice(emoji="🎯")
    except Exception:
        await message.answer("📊")


@router.message(Command("stat", "stats"))
async def user_stat_handler(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await message.answer("Доступ запрещен.")
        return
    await state.clear()
    await send_stats(message)


@router.message(StateFilter("*"), F.text == "Статистика пользователей")
async def stats_button_handler(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    await send_stats(message)


@router.message(StateFilter("*"), F.text == "Последние лиды")
async def latest_leads_handler(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()
    if Lead is None:
        await message.answer("Модель Lead отключена в db/models.py, список лидов недоступен.")
        return

    async with async_session() as session:
        result = await session.execute(
            select(Lead).order_by(Lead.created_at.desc(), Lead.id.desc()).limit(10)
        )
        leads = result.scalars().all()

    if not leads:
        await message.answer("Лидов пока нет.")
        return

    lines = ["Последние лиды:"]
    for lead in leads:
        phone = getattr(lead, "phone", None) or "-"
        lines.append(
            f"#{lead.id} | {lead.action} | {lead.user_telegram_id} | "
            f"{phone} | {lead.created_at.strftime('%Y-%m-%d %H:%M:%S')} UTC"
        )
    await message.answer("\n".join(lines))


@router.message(StateFilter("*"), F.text == "Канал авто в пути")
async def auto_in_path_channel_settings_handler(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        return
    await state.clear()

    channel_record = await get_channel_record(AUTO_IN_PATH_CHANNEL_CODE)
    current_chat_id = getattr(channel_record, "chat_id", None) if channel_record else None
    current_title = getattr(channel_record, "title", None) if channel_record else None
    current_chat_id_text = str(current_chat_id) if current_chat_id is not None else "не задан"
    title_line = f"\nНазвание: {current_title}" if current_title else ""

    await state.set_state(AdminStates.waiting_auto_in_path_channel_id)
    await message.answer(
        "Настройка канала «Авто в пути».\n"
        f"Текущий ID: {current_chat_id_text}{title_line}\n\n"
        "Отправьте новый ID канала/группы (например `-1003706573371`).\n"
        "Внимание: при смене ID все сохранённые посты «Авто в пути» в БД будут обнулены.",
        parse_mode="Markdown",
        reply_markup=get_admin_keyboard(),
    )


@router.message(AdminStates.waiting_auto_in_path_channel_id)
async def auto_in_path_channel_save_handler(message: types.Message, state: FSMContext):
    if not is_admin(message.from_user.id):
        await state.clear()
        return

    raw_value = (message.text or "").strip()
    if not raw_value:
        await message.answer(
            "Отправьте числовой ID канала, например `-1003706573371`.",
            parse_mode="Markdown",
        )
        return

    try:
        new_chat_id = int(raw_value)
    except ValueError:
        await message.answer(
            "Неверный формат. Нужен числовой ID канала, например `-1003706573371`.",
            parse_mode="Markdown",
        )
        return

    current_record = await get_channel_record(AUTO_IN_PATH_CHANNEL_CODE)
    current_chat_id = getattr(current_record, "chat_id", None) if current_record else None
    channel_changed = current_chat_id is None or int(current_chat_id) != new_chat_id

    await set_auto_in_path_channel_id(new_chat_id, title="Авто в пути")
    deleted_posts = 0
    if channel_changed:
        deleted_posts = await clear_auto_in_transit_posts_db()

    await state.clear()
    text = f"Канал «Авто в пути» обновлён: `{new_chat_id}`"
    if channel_changed:
        text += f"\nПосты в БД обнулены: `{deleted_posts}`"
    await message.answer(text, parse_mode="Markdown", reply_markup=get_admin_keyboard())


