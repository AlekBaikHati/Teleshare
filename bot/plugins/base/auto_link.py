import asyncio
import uuid
from typing import ClassVar

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import config
from bot.database import MongoDB
from bot.options import options
from bot.utilities.helpers import DataEncoder, RateLimiter
from bot.utilities.pyrofilters import ConvoMessage, PyroFilters
from bot.utilities.pyrotools import FileResolverModel


class AutoLinkGen:
    database = MongoDB()
    background_tasks: ClassVar[set[asyncio.Task]] = set()
    files_cache: ClassVar[dict[int, dict[int, list[FileResolverModel]]]] = {}

    @classmethod
    async def process_files(
        cls,
        client: Client,
        message: Message,
        file_data: list[FileResolverModel],
    ) -> Message:
        "Mengatur cadangan file"

        unique_link = f"{uuid.uuid4().int}"
        file_link = DataEncoder.encode_data(unique_link)
        file_origin = config.BACKUP_CHANNEL if options.settings.BACKUP_FILES else message.chat.id
        file_datas = [i.model_dump() for i in file_data]

        add_file = await cls.database.add_file(file_link=file_link, file_origin=file_origin, file_data=file_datas)

        if add_file:
            link = f"https://t.me/{client.me.username}?start={file_link}"  # type: ignore[reportOptionalMemberAccess]
            reply_markup = InlineKeyboardMarkup(
                [[InlineKeyboardButton("Share URL", url=f"https://t.me/share/url?url={link}")]],
            )

            photo_url = config.LINK_PHOTO
            caption = f">Inilah tautan Anda:\n{link}"

            return await message.reply_photo(
                photo=photo_url,
                caption=caption,
                quote=True,
                reply_markup=reply_markup,
            )

        return await message.reply("Tidak bisa menambahkan file ke basis data")

    @classmethod
    async def media_group_handler(cls, client: Client, message: Message) -> None:
        "Penanganan grup media"
        await asyncio.sleep(3)
        file_datas = [i.model_dump() for i in cls.files_cache[message.from_user.id][message.media_group_id]]

        if options.settings.BACKUP_FILES:
            forwarded_messages = await client.forward_messages(
                chat_id=config.BACKUP_CHANNEL,
                from_chat_id=message.chat.id,
                message_ids=[i["message_id"] for i in file_datas],
                hide_sender_name=True,
            )
            file_datas = [
                FileResolverModel(
                    caption=msg.caption.markdown if msg.caption else None,
                    file_id=(msg.document or msg.video or msg.photo or msg.audio or msg.sticker).file_id,
                    message_id=msg.id,
                    media_group_id=msg.media_group_id,
                )
                for msg in (forwarded_messages if isinstance(forwarded_messages, list) else [forwarded_messages])
            ]
        else:
            file_datas = [FileResolverModel(**d) for d in file_datas]

        del cls.files_cache[message.from_user.id][message.media_group_id]
        await cls.process_files(client=client, message=message, file_data=file_datas)

    @classmethod
    async def handle_files(cls, client: Client, message: Message) -> None:
        "Mengatur file"
        file_type = message.document or message.video or message.photo or message.audio or message.sticker
        message_id = message.id
        user_id = message.from_user.id

        resolve_file = FileResolverModel(
            caption=message.caption.markdown if message.caption else None,
            file_id=file_type.file_id,
            message_id=message_id,
        )

        if message.media_group_id:
            if not cls.files_cache.get(user_id, {}).get(message.media_group_id):
                cls.files_cache[user_id] = {message.media_group_id: []}
                task = asyncio.create_task(cls.media_group_handler(client=client, message=message))
                cls.background_tasks.add(task)
                task.add_done_callback(cls.background_tasks.discard)

            resolve_file.media_group_id = message.media_group_id
            cls.files_cache[user_id][message.media_group_id].append(resolve_file)
        else:
            if options.settings.BACKUP_FILES:
                backup_file = await message.copy(chat_id=config.BACKUP_CHANNEL)
                resolve_file.message_id = backup_file[0].id if isinstance(backup_file, list) else backup_file.id

            await cls.process_files(client=client, message=message, file_data=[resolve_file])


@Client.on_message(
    filters.private
    & PyroFilters.admin(allow_global=True)
    & PyroFilters.subscription()
    & PyroFilters.user_not_in_conversation()
    & (filters.audio | filters.photo | filters.video | filters.document | filters.sticker),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def auto_link_gen(client: Client, message: ConvoMessage) -> Message | None:
    """Mengatur file yang dikirim atau diteruskan langsung ke bot dan menghasilkan tautan untuk itu."""

    if getattr(client.me, "id", None) == message.from_user.id or not config.AUTO_GENERATE_LINK:
        return None

    await AutoLinkGen.handle_files(client=client, message=message)
