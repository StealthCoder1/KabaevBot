from tgBot.bot.shared import *


async def _broadcast_source_post(message: types.Message, bot: Bot):
    source_chat_id = message.chat.id
    broadcast_source_channel_id = await get_broadcast_source_channel_id()
    auto_in_path_channel_id = await get_auto_in_path_channel_id()
    allowed_sources = {
        cid for cid in (broadcast_source_channel_id, auto_in_path_channel_id) if cid is not None
    }
    if source_chat_id not in allowed_sources:
        return

    if auto_in_path_channel_id and source_chat_id == auto_in_path_channel_id:
        await save_auto_in_transit_post(message)

    async with async_session() as session:
        result = await session.execute(select(User.telegram_id))
        user_ids = _normalize_user_ids(result.all())

    if not user_ids:
        return

    if source_chat_id == broadcast_source_channel_id and await handle_sold_post(message, user_ids, bot):
        return

    if message.media_group_id:
        await handle_media_group(message, user_ids, bot)
    else:
        await handle_single_message(message, user_ids, bot)


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
                logger.error(f"Ошибка отправки уведомления пользователю {user_id}: {exc}")

        return True
    return False


async def handle_media_group(message: types.Message, user_ids, bot: Bot):
    key = (message.chat.id, message.media_group_id)
    media_groups_buffer[key].append(message)
    await asyncio.sleep(0.5)
    media_messages = media_groups_buffer.pop(key, [])
    if not media_messages:
        return

    media_cache[message.media_group_id] = media_messages

    media_to_send = [
        types.InputMediaPhoto(media=msg.photo[-1].file_id, caption=msg.caption or "")
        if msg.photo
        else types.InputMediaVideo(media=msg.video.file_id, caption=msg.caption or "")
        for msg in media_messages
    ]

    for user_id in user_ids:
        try:
            await bot.send_media_group(chat_id=user_id, media=media_to_send)
        except Exception as exc:
            logger.error(f"Ошибка отправки медиа-группы пользователю {user_id}: {exc}")


async def handle_single_message(message: types.Message, user_ids, bot: Bot):
    for user_id in user_ids:
        try:
            await send_message_by_type(bot, user_id, message)
        except Exception as exc:
            logger.error(f"Ошибка отправки сообщения пользователю {user_id}: {exc}")


async def send_message_by_type(bot: Bot, user_id, message: types.Message):
    if message.photo:
        await bot.send_photo(
            chat_id=user_id,
            photo=message.photo[-1].file_id,
            caption=message.caption or "",
        )
    elif message.video:
        await bot.send_video(
            chat_id=user_id,
            video=message.video.file_id,
            caption=message.caption or "",
        )
    elif message.text:
        await bot.send_message(chat_id=user_id, text=message.text)
    else:
        await bot.copy_message(
            chat_id=user_id,
            from_chat_id=message.chat.id,
            message_id=message.message_id,
        )
