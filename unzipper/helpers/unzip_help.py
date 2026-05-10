# Copyright (c) 2022 - 2024 UnxTar
import math
import time

from asyncio import sleep
from pyrogram.errors import FloodWait, MessageNotModified
from unzipper import LOGGER
from unzipper.helpers.database import del_cancel_task, get_cancel_task
from unzipper.modules.bot_data import Buttons, Messages


_last_progress_update = {}


class TransferCancelled(Exception):
    pass


async def progress_for_pyrogram(current, total, ud_type, message, start, unzip_bot):
    now = time.time()
    diff = now - start

    # Throttle cancel-task DB check to once per 3 seconds
    msg_id = message.id
    last_update = _last_progress_update.get(msg_id, 0)

    if message.from_user is not None and (now - last_update) >= 3:
        if await get_cancel_task(message.from_user.id):
            _last_progress_update.pop(msg_id, None)
            await message.edit(text=Messages.DL_STOPPED)
            await del_cancel_task(message.from_user.id)
            raise TransferCancelled(Messages.DL_STOPPED)

    # Update progress every 5 seconds or at completion
    if current == total or (now - last_update) >= 5:
        _last_progress_update[msg_id] = now

        if total == 0:
            tmp = Messages.UNKNOWN_SIZE
            try:
                await message.edit(
                    text=Messages.PROGRESS_MSG.format(ud_type, tmp),
                    reply_markup=Buttons.I_PREFER_STOP,
                )
            except FloodWait as f:
                await sleep(f.value)
            except:
                pass
        else:
            percentage = current * 100 / total
            if diff == 0:
                speed = 0
                estimated_total_time = "0 s"
            else:
                speed = current / diff
                time_to_completion = round((total - current) / speed) * 1000
                estimated_total_time = TimeFormatter(milliseconds=time_to_completion)
            progress = f'[{"".join(["⬢" for i in range(math.floor(percentage / 5))])}{"".join(["⬡" for i in range(20 - math.floor(percentage / 5))])}] \n{Messages.PROCESSING} : `{round(percentage, 2)}%`\n'
            tmp = (
                progress
                + f'`{humanbytes(current)} of {humanbytes(total)}`\n{Messages.SPEED} `{humanbytes(speed)}/s`\n{Messages.ETA} `{estimated_total_time if estimated_total_time != "" else "0 s"}`\n'
            )
            try:
                await message.edit(
                    text=Messages.PROGRESS_MSG.format(ud_type, tmp),
                    reply_markup=Buttons.I_PREFER_STOP,
                )
            except FloodWait as f:
                await sleep(f.value)
            except MessageNotModified:
                pass
            except Exception as e:
                LOGGER.warning(f"Progress update failed: {e}")

        # Clean up tracking when transfer completes
        if current == total:
            _last_progress_update.pop(msg_id, None)


_last_progress_url_update = {}


async def progress_urls(current, total, ud_type, message, start):
    now = time.time()
    diff = now - start
    msg_id = message.id
    last_update = _last_progress_url_update.get(msg_id, 0)

    if current == total or (now - last_update) >= 5:
        _last_progress_url_update[msg_id] = now
        percentage = current * 100 / total
        if diff == 0:
            speed = 0
            estimated_total_time = "0 s"
        else:
            speed = current / diff
            time_to_completion = round((total - current) / speed) * 1000
            estimated_total_time = TimeFormatter(milliseconds=time_to_completion)
        progress = f'[{"".join(["⬢" for i in range(math.floor(percentage / 5))])}{"".join(["⬡" for i in range(20 - math.floor(percentage / 5))])}] \n{Messages.PROCESSING} : `{round(percentage, 2)}%`\n'
        tmp = (
            progress
            + f'{Messages.ETA} `{estimated_total_time if estimated_total_time != "" else "0 s"}`\n'
        )
        try:
            await message.edit(Messages.PROGRESS_MSG.format(ud_type, tmp))
        except FloodWait as f:
            await sleep(f.value)
        except MessageNotModified:
            pass
        except Exception as e:
            LOGGER.warning(f"Progress URL update failed: {e}")

        if current == total:
            _last_progress_url_update.pop(msg_id, None)


def humanbytes(size):
    if not size:
        return ""
    power = 2**10
    n = 0
    Dic_powerN = {0: " ", 1: "Ki", 2: "Mi", 3: "Gi", 4: "Ti"}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN.get(n) + "B"


def TimeFormatter(milliseconds: int) -> str:
    seconds, milliseconds = divmod(int(milliseconds), 1000)
    minutes, seconds = divmod(seconds, 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
        + ((str(milliseconds) + "ms, ") if milliseconds else "")
    )
    return tmp[:-2]


def timeformat_sec(seconds: int) -> str:
    minutes, seconds = divmod(int(seconds), 60)
    hours, minutes = divmod(minutes, 60)
    days, hours = divmod(hours, 24)
    tmp = (
        ((str(days) + "d, ") if days else "")
        + ((str(hours) + "h, ") if hours else "")
        + ((str(minutes) + "m, ") if minutes else "")
        + ((str(seconds) + "s, ") if seconds else "")
    )
    return tmp[:-2]


# List of common extentions
extentions_list = {
    "archive": [
        "7z",
        "apk",
        "apkm",
        "apks",
        "appx",
        "arc",
        "bcm",
        "bin",
        "br",
        "bz2",
        "dmg",
        "exe",
        "gz",
        "img",
        "ipsw",
        "iso",
        "jar",
        "lz4",
        "msi",
        "paf",
        "pak",
        "pea",
        "pkg",
        "rar",
        "tar",
        "tgz",
        "wim",
        "x7",
        "xapk",
        "xz",
        "z",
        "zip",
        "zipx",
        "zpaq",
        "zst",
        "zstd",
    ],
    "audio": ["aac", "aif", "aiff", "alac", "flac", "m4a", "mp3", "ogg", "wav", "wma"],
    "photo": ["gif", "jpg", "jpeg", "png", "tiff", "webp"],
    "split": ["0*", "001", "002", "003", "004", "005", "006", "007", "008", "009"],
    "video": ["3gp", "avi", "flv", "mp4", "mkv", "mov", "mpeg", "mpg", "webm"],
}
