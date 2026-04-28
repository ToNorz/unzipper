# Copyright (c) 2022 - 2024 UnxTar
from pyrogram import enums
from pyrogram.errors import UserNotParticipant
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup

from config import Config
from unzipper import LOGGER


FSUB_CHATS = [
    ("CoupOrg", "📢 Channel"),
    ("CoupChats", "💬 Group"),
]


JOIN_TEXT = (
    "🔒 **Access locked**\n\n"
    "To use this bot you must join our channel **and** group :\n"
    "• Channel — @CoupOrg\n"
    "• Group — @CoupChats\n\n"
    "Join both, then tap **Verify ✓**"
)

JOIN_TEXT_OK = "✅ **You're verified !** You can now use the bot."


def join_buttons():
    rows = [
        [InlineKeyboardButton(label, url=f"https://t.me/{chat}")]
        for chat, label in FSUB_CHATS
    ]
    rows.append([InlineKeyboardButton("Verify ✓", callback_data="verifysub")])
    return InlineKeyboardMarkup(rows)


async def _is_in_chat(client, chat, user_id):
    try:
        member = await client.get_chat_member(chat, user_id)
    except UserNotParticipant:
        return False
    except Exception as e:
        LOGGER.warning(
            "Force-sub check failed for chat=%s user=%s : %s. Allowing through.",
            chat,
            user_id,
            e,
        )
        return True
    return member.status not in (
        enums.ChatMemberStatus.LEFT,
        enums.ChatMemberStatus.BANNED,
    )


async def is_user_subscribed(client, user_id):
    if user_id == Config.BOT_OWNER:
        return True
    for chat, _ in FSUB_CHATS:
        if not await _is_in_chat(client, chat, user_id):
            return False
    return True
