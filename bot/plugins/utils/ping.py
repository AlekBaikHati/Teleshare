from pyrogram import filters
from pyrogram.client import Client
import time  # Import time untuk menghitung uptime
import asyncio
from bot.utilities.pyrotools import HelpCmd  # Pastikan ini ada
import datetime  # Import datetime untuk format waktu

# Menyimpan waktu mulai bot
START_TIME = time.time()
START_DATETIME = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")  # Format waktu mulai

@Client.on_message(filters.command("ping") & filters.private)
async def ping(client: Client, message):
    """Mengukur waktu ping dan uptime bot."""

    # Menghitung uptime
    uptime = time.time() - START_TIME
    days = int(uptime // (24 * 3600))
    hours = int((uptime % (24 * 3600)) // 3600)
    minutes = int((uptime % 3600) // 60)
    seconds = int(uptime % 60)
    uptime_str = f"{days} days {hours} hours {minutes} minutes {seconds} seconds"

    # Mengukur ping
    start_time = time.time()
    ping_message = await message.reply("Pong... 🏓")  # Mengirim pesan sementara dengan emoji pingpong
    ping_time = (time.time() - start_time) * 1000  # Hitung waktu ping

    # Kirim hasil ping, uptime, dan Active Since
    await asyncio.sleep(2)
    await ping_message.edit(
        f"✦•┈๑⋅⋯ ⋯⋅๑┈•✦\n"
        f">**Ping:** `{ping_time:.2f} ms`\n"
        f">**Uptime:** `{uptime_str}`\n"
        f">**Active Since:** `{START_DATETIME}`\n"  # Menambahkan Active Since
        f"✦•┈๑⋅⋯ ⋯⋅๑┈•✦"
    )
    # Menghapus pesan ping sementara setelah 5 detik
    #await asyncio.sleep(10)  # Tunggu 5 detik sebelum menghapus pesan
    #await ping_message.delete()  # Menghapus pesan ping sementara
    HelpCmd.set_help(
        command="ping",
        description=ping.__doc__,
        allow_global=True,
        allow_non_admin=True,
    )
