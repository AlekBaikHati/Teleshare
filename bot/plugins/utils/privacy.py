from pyrogram import filters
from pyrogram.client import Client
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup, Message, WebAppInfo

from bot.utilities.helpers import RateLimiter
from bot.utilities.pyrotools import HelpCmd


@Client.on_message(
    filters.private & filters.command("privacy"),
)
@RateLimiter.hybrid_limiter(func_count=1)
async def privacy(_: Client, message: Message) -> Message:
    """Display bot privacy"""

    return await message.reply(
        text="Privacy Policy\nLast Updated: July 04, 2024\n\n"
        "This Privacy Policy explains how we collect, use, and protect your information when you use our bot.\n\n"
        "1. Information We Collect\n"
        ">1.1 Personal Information\n"
        ">- We do not collect any personal information such as your name, email address, or phone number.\n\n"
        ">1.2 Usage Data\n"
        ">- We may collect information about your interactions with the bot, such as messages sent, commands used, and the time and date of your interactions.\n\n"
        "2. How We Use Your Information\n"
        ">2.1 To Operate the Bot\n"
        ">- The information collected is used to operate and improve the functionality of the bot.\n\n"
        ">2.2 To Improve Our Services\n"
        ">- We may use the information to analyze how users interact with the bot in order to improve our services.\n\n"
        "3. Data Security\n"
        ">3.1 Security Measures\n"
        ">- We implement appropriate technical and organizational measures to protect your information from unauthorized access, disclosure, alteration, or destruction.\n\n"
        "4. Data Sharing and Disclosure\n"
        ">4.1 Third-Party Services\n"
        ">- We do not share your information with third parties, except as required by law or to protect our rights.\n\n"
        "5. Your Data Protection Rights\n"
        ">5.1 Access and Control\n"
        ">- You have the right to request access to the information we have collected about you. You also have the right to request that we correct or delete your data.\n\n"
        "6. Changes to This Privacy Policy\n"
        ">6.1 Updates\n"
        ">- We may update our Privacy Policy from time to time. We will notify you of any changes by posting the new Privacy Policy on this page.\n\n"
        "7. Contact Us\n"
        ">7.1 Contact Information\n"
        ">- If you have any questions about this Privacy Policy, please contact us on the button below.\n\n"
        "Note:\n"
        ">- It's important to review this policy with a legal professional to ensure compliance with relevant laws and regulations.\n\n"
        "Created bot by: - \nSource Code: -",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        text="PRIVACY POLICY",
                        web_app=WebAppInfo(url="https://i.ibb.co.com/qYjLjG3T/image.png"),
                    ),
                ],
            ],
        ),
    )


HelpCmd.set_help(
    command="privacy",
    description=privacy.__doc__,
    allow_global=True,
    allow_non_admin=True,
)
