from tgBot.bot.shared import *


MEDIA_GROUP_FLUSH_DELAY_SECONDS = 2.5
AUTO_IN_PATH_BATCH_FLUSH_DELAY_SECONDS = 8.0
media_group_broadcast_tasks = {}
auto_in_path_batch_buffer = {}
auto_in_path_batch_tasks = {}


def _log_media_group_task_result(task) -> None:
    try:
        task.result()
    except asyncio.CancelledError:
        pass
    except Exception as exc:
        logger.error(f"Ошибка обработки медиагруппы для рассылки: {exc}")


def _log_auto_in_path_batch_task_result(task) -> None:
    try:
        task.result()
    except asyncio.CancelledError:
        pass
    except Exception as exc:
        logger.error(f"Ошибка обработки пакета авто в пути: {exc}")


async def _broadcast_source_post(message: types.Message, bot: Bot):
    source_chat_id = message.chat.id
    broadcast_source_channel_id = await get_broadcast_source_channel_id()
    auto_in_path_channel_id = await get_auto_in_path_channel_id()
    is_auto_in_path_post = bool(auto_in_path_channel_id and source_chat_id == auto_in_path_channel_id)

    if is_auto_in_path_post:
        await save_auto_in_transit_post(message)
        await handle_auto_in_path_message_batch(message, bot)
        return
    elif broadcast_source_channel_id is None or source_chat_id != broadcast_source_channel_id:
        return

    if message.media_group_id:
        await handle_media_group(message, bot, is_auto_in_path_post=is_auto_in_path_post)
        return

    user_ids = await get_known_user_ids(exclude_user_ids={bot.id})
    if not user_ids:
        return

    if not is_auto_in_path_post and await handle_sold_post(message, user_ids, bot):
        return

    await handle_single_message(message, user_ids, bot, is_auto_in_path_post=is_auto_in_path_post)


@router.channel_post()
async def universal_channel_handler(message: types.Message, bot: Bot):
    await _broadcast_source_post(message, bot)


@router.message(F.chat.type == "supergroup")
@router.message(F.chat.type == "group")
async def auto_in_path_group_message_handler(message: types.Message, bot: Bot):
    auto_in_path_channel_id = await get_auto_in_path_channel_id()
    if auto_in_path_channel_id is None or message.chat.id != auto_in_path_channel_id:
        return
    await _broadcast_source_post(message, bot)


async def handle_sold_post(message: types.Message, user_ids, bot: Bot):
    sold_words = ("продано",)
    text = message.text or message.caption or ""

    if any(word.lower() == text.strip().lower() for word in sold_words):
        if not message.reply_to_message:
            return False

        original = message.reply_to_message
        media_to_send = []

        if original.media_group_id:
            group_id = original.media_group_id
            group_messages = media_cache.get(group_id, [original])
            for msg in group_messages:
                if msg.photo:
                    media_to_send.append(
                        types.InputMediaPhoto(media=msg.photo[-1].file_id, caption=msg.caption or "")
                    )
                elif msg.video:
                    media_to_send.append(
                        types.InputMediaVideo(media=msg.video.file_id, caption=msg.caption or "")
                    )
        else:
            if original.photo:
                media_to_send.append(
                    types.InputMediaPhoto(media=original.photo[-1].file_id, caption=original.caption or "")
                )
            elif original.video:
                media_to_send.append(
                    types.InputMediaVideo(media=original.video.file_id, caption=original.caption or "")
                )

        for user_id in user_ids:
            try:
                if media_to_send:
                    if len(media_to_send) == 1:
                        media = media_to_send[0]
                        if isinstance(media, types.InputMediaPhoto):
                            await bot.send_photo(chat_id=user_id, photo=media.media, caption=media.caption or "")
                        else:
                            await bot.send_video(chat_id=user_id, video=media.media, caption=media.caption or "")
                    else:
                        await bot.send_media_group(chat_id=user_id, media=media_to_send)
                await bot.send_message(chat_id=user_id, text="Машина из поста ПРОДАНА!")
            except Exception as exc:
                await handle_user_delivery_error(user_id, exc, action="отправить уведомление о продаже")

        return True
    return False


async def _get_auto_in_path_next_post_index_for_latest() -> int | None:
    batches = await get_auto_in_transit_copy_batches(newest_first=True)
    return 1 if len(batches) > 1 else None


async def handle_auto_in_path_message_batch(message: types.Message, bot: Bot):
    key = message.chat.id
    messages_by_id = auto_in_path_batch_buffer.setdefault(key, {})
    messages_by_id[message.message_id] = message

    pending_task = auto_in_path_batch_tasks.get(key)
    if pending_task and not pending_task.done():
        pending_task.cancel()

    task = asyncio.create_task(_flush_auto_in_path_batch_after_delay(key, bot))
    task.add_done_callback(_log_auto_in_path_batch_task_result)
    auto_in_path_batch_tasks[key] = task


async def _send_auto_in_path_batch_to_user(
    bot: Bot,
    user_id: int,
    messages: list[types.Message],
) -> int | None:
    if not messages:
        return None

    source_chat_id = messages[0].chat.id
    message_ids = [message.message_id for message in messages]

    try:
        copied_messages = await bot.copy_messages(
            chat_id=user_id,
            from_chat_id=source_chat_id,
            message_ids=message_ids,
        )
        return next(
            (
                copied_id
                for copied_id in reversed([_copied_message_id(item) for item in copied_messages])
                if copied_id is not None
            ),
            None,
        )
    except Exception as exc:
        logger.warning(
            f"Не удалось скопировать пакет авто в пути одним вызовом пользователю {user_id}, "
            f"пробую по одному: {exc}"
        )

    reply_to_message_id = None
    for message_id in message_ids:
        copied_message = await bot.copy_message(
            chat_id=user_id,
            from_chat_id=source_chat_id,
            message_id=message_id,
        )
        reply_to_message_id = _copied_message_id(copied_message) or reply_to_message_id

    return reply_to_message_id


async def _flush_auto_in_path_batch_after_delay(key, bot: Bot):
    try:
        await asyncio.sleep(AUTO_IN_PATH_BATCH_FLUSH_DELAY_SECONDS)
    except asyncio.CancelledError:
        return

    messages_by_id = auto_in_path_batch_buffer.pop(key, {})
    auto_in_path_batch_tasks.pop(key, None)
    messages = sorted(messages_by_id.values(), key=lambda msg: msg.message_id)
    if not messages:
        return

    source_chat_id = messages[0].chat.id
    source_message_id = messages[0].message_id
    message_ids = [message.message_id for message in messages]
    if len(message_ids) > 1:
        batch_group_id = f"auto_in_path_batch:{source_chat_id}:{source_message_id}:{message_ids[-1]}"
        await set_auto_in_transit_posts_media_group_id(
            source_chat_id,
            message_ids,
            batch_group_id,
        )

    user_ids = await get_known_user_ids(exclude_user_ids={bot.id})
    if not user_ids:
        return

    auto_in_path_next_post_index = await _get_auto_in_path_next_post_index_for_latest()
    for user_id in user_ids:
        try:
            reply_to_message_id = await _send_auto_in_path_batch_to_user(bot, user_id, messages)
            await _send_auto_in_path_actions_prompt(
                bot,
                user_id,
                source_chat_id,
                source_message_id,
                next_post_index=auto_in_path_next_post_index,
                reply_to_message_id=reply_to_message_id,
            )
        except Exception as exc:
            await handle_user_delivery_error(user_id, exc, action="отправить авто в пути")


async def handle_media_group(message: types.Message, bot: Bot, *, is_auto_in_path_post: bool = False):
    key = (message.chat.id, message.media_group_id)
    media_groups_buffer[key].append(message)
    pending_task = media_group_broadcast_tasks.get(key)
    if pending_task and not pending_task.done():
        pending_task.cancel()

    task = asyncio.create_task(
        _flush_media_group_after_delay(
            key,
            bot,
            is_auto_in_path_post=is_auto_in_path_post,
        )
    )
    task.add_done_callback(_log_media_group_task_result)
    media_group_broadcast_tasks[key] = task


async def _flush_media_group_after_delay(key, bot: Bot, *, is_auto_in_path_post: bool = False):
    try:
        await asyncio.sleep(MEDIA_GROUP_FLUSH_DELAY_SECONDS)
    except asyncio.CancelledError:
        return

    media_messages = media_groups_buffer.pop(key, [])
    media_group_broadcast_tasks.pop(key, None)
    if not media_messages:
        return

    media_messages.sort(key=lambda msg: msg.message_id)
    source_chat_id = key[0]
    media_group_id = key[1]
    media_cache[media_group_id] = media_messages
    source_message_id = min(msg.message_id for msg in media_messages)

    media_to_send = []
    for msg in media_messages:
        if msg.photo:
            media_to_send.append(
                types.InputMediaPhoto(media=msg.photo[-1].file_id, caption=msg.caption or "")
            )
        elif msg.video:
            media_to_send.append(
                types.InputMediaVideo(media=msg.video.file_id, caption=msg.caption or "")
            )

    if not media_to_send:
        return

    user_ids = await get_known_user_ids(exclude_user_ids={bot.id})
    if not user_ids:
        return

    auto_in_path_next_post_index = None
    if is_auto_in_path_post:
        auto_in_path_next_post_index = await _get_auto_in_path_next_post_index_for_latest()

    for user_id in user_ids:
        try:
            sent_messages = await bot.send_media_group(chat_id=user_id, media=media_to_send)
            reply_to_message_id = next(
                (
                    sent_message.message_id
                    for sent_message in sent_messages
                    if getattr(sent_message, "message_id", None) is not None
                ),
                None,
            )
            if is_auto_in_path_post:
                await _send_auto_in_path_actions_prompt(
                    bot,
                    user_id,
                    source_chat_id,
                    source_message_id,
                    next_post_index=auto_in_path_next_post_index,
                    reply_to_message_id=reply_to_message_id,
                )
                continue

            attached = False
            for sent_message in sent_messages:
                attached = await _attach_post_actions_keyboard_to_message(
                    bot,
                    user_id,
                    sent_message,
                    source_chat_id,
                    source_message_id,
                    log_failures=False,
                )
                if attached:
                    break

            if not attached:
                await _send_post_actions_prompt(
                    bot,
                    user_id,
                    source_chat_id,
                    source_message_id,
                    reply_to_message_id=reply_to_message_id,
                )
        except Exception as exc:
            await handle_user_delivery_error(user_id, exc, action="отправить медиа-группу")


async def handle_single_message(message: types.Message, user_ids, bot: Bot, *, is_auto_in_path_post: bool = False):
    auto_in_path_next_post_index = None
    if is_auto_in_path_post:
        auto_in_path_next_post_index = await _get_auto_in_path_next_post_index_for_latest()

    for user_id in user_ids:
        try:
            sent_message = await send_message_by_type(
                bot,
                user_id,
                message,
                with_post_actions=not is_auto_in_path_post,
            )
            if is_auto_in_path_post:
                await _send_auto_in_path_actions_prompt(
                    bot,
                    user_id,
                    message.chat.id,
                    message.message_id,
                    next_post_index=auto_in_path_next_post_index,
                    reply_to_message_id=_copied_message_id(sent_message),
                )
        except Exception as exc:
            await handle_user_delivery_error(user_id, exc, action="отправить сообщение")


async def send_message_by_type(
    bot: Bot,
    user_id,
    message: types.Message,
    *,
    with_post_actions: bool = True,
):
    reply_markup = (
        get_post_actions_keyboard(message.chat.id, message.message_id)
        if with_post_actions
        else None
    )
    if message.photo:
        return await bot.send_photo(
            chat_id=user_id,
            photo=message.photo[-1].file_id,
            caption=message.caption or "",
            reply_markup=reply_markup,
        )
    elif message.video:
        return await bot.send_video(
            chat_id=user_id,
            video=message.video.file_id,
            caption=message.caption or "",
            reply_markup=reply_markup,
        )
    elif message.text:
        return await bot.send_message(chat_id=user_id, text=message.text, reply_markup=reply_markup)
    else:
        return await bot.copy_message(
            chat_id=user_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
            reply_markup=reply_markup,
        )
