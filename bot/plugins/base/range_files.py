import uuid
from inspect import cleandoc

from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message

from bot.config import config
from bot.database import MongoDB
from bot.utilities.helpers import DataEncoder, RateLimiter
from bot.utilities.pyrofilters import ConvoMessage, PyroFilters
from bot.utilities.pyrotools import HelpCmd

database = MongoDB()


@Client.on_message(
    filters.private & PyroFilters.admin() & filters.command("range_files"),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def range_files(client: Client, message: ConvoMessage) -> Message | None:
    """>**Mengambil file langsung dari saluran cadangan untuk membuat tautan yang dapat dibagikan dari id file yang berurutan.**

    **Penggunaan:**
        /range_files [tautan awal] [tautan akhir] [(opsional) id yang dikecualikan]

        /range_files https://t.me/c/-100/9 https://t.me/c/-100/100

        /range_files https://t.me/c/-100/9 https://t.me/c/-100/100 69 70 80 90

    >Ini mengambil file dari basis data mulai dari id file 9 hingga 100 dan mengkecualikan 69, 79, 80, dan 90
    """

    if not message.command[2:]:
        return await message.reply(cleandoc(range_files.__doc__ or ""))

    start_file_link = message.command[1].split("/")

    if start_file_link[-2] != str(config.BACKUP_CHANNEL).removeprefix("-100"):
        return await message.reply(text="Hanya kirim tautan file dari saluran basis data Anda saat ini", quote=True)

    end_file_link = message.command[2].split("/")
    exclude_file_ids = set(map(int, message.command[3:]))

    file_ids_range = [
        num for num in range(int(start_file_link[-1]), int(end_file_link[-1]) + 1) if num not in exclude_file_ids
    ]

    fetch_files = await client.get_messages(chat_id=config.BACKUP_CHANNEL, message_ids=file_ids_range)
    fetch_files = [fetch_files] if not isinstance(fetch_files, list) else fetch_files

    files_to_store = []
    for file in fetch_files:
        file_type = file.document or file.video or file.photo or file.audio or file.sticker

        if not file_type or file.empty:
            continue

        files_to_store.append(
            {
                "caption": file.caption.markdown if file.caption else None,
                "file_id": file_type.file_id,
                "message_id": file.id,
            },
        )

    if not files_to_store:
        return await message.reply(text="Tidak bisa mengambil file dari rentang yang diberikan.", quote=True)

    unique_link = f"{uuid.uuid4().int}"
    file_link = DataEncoder.encode_data(unique_link)
    file_origin = config.BACKUP_CHANNEL

    add_file = await database.add_file(file_link=file_link, file_origin=file_origin, file_data=files_to_store)

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
    return await message.reply(text="Tidak bisa menambahkan file ke basis data", quote=True)


HelpCmd.set_help(
    command="range_files",
    description=range_files.__doc__,
    allow_global=False,
    allow_non_admin=False,
)
