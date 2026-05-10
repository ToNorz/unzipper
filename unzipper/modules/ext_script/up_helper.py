# Copyright (c) 2022 - 2024 UnxTar
import asyncio
import os
import pathlib
import re
import shutil
import subprocess
import zipfile

from datetime import timedelta
from time import time
from pyrogram.errors import FloodWait, PhotoExtInvalid, PhotoSaveFileInvalid

from config import Config
from unzipper import LOGGER, unzipperbot
from unzipper.helpers.database import get_upload_mode
from unzipper.helpers.unzip_help import (
    extentions_list,
    progress_for_pyrogram,
    progress_urls,
)
from unzipper.modules.bot_data import Messages
from unzipper.modules.ext_script.custom_thumbnail import thumb_exists
from unzipper.modules.ext_script.metadata_helper import get_audio_metadata


# To get video duration and thumbnail
async def run_shell_cmds(command):
    run = subprocess.Popen(
        command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True
    )
    shell_output = run.stdout.read()[:-1].decode("utf-8").rstrip(
        "\n"
    ) + run.stderr.read()[:-1].decode("utf-8").rstrip("\n")
    LOGGER.info("shell_output : " + shell_output)
    if run.stderr:
        run.stderr.close()
    if run.stdout:
        run.stdout.close()
    return shell_output


# Get file size
async def get_size(doc_f):
    try:
        fsize = os.stat(doc_f).st_size
        return fsize
    except:
        return -1


def _zip_for_upload(source, destination):
    with zipfile.ZipFile(
        destination, "w", compression=zipfile.ZIP_STORED, allowZip64=True
    ) as zip_file:
        zip_file.write(source, arcname=os.path.basename(source))


# Send file to a user
async def send_file(unzip_bot, c_id, doc_f, query, full_path, log_msg, split):
    fsize = await get_size(doc_f)
    if fsize in (-1, 0):  # File not found or empty
        try:
            await unzipperbot.send_message(
                c_id, Messages.EMPTY_FILE.format(os.path.basename(doc_f))
            )
        except:
            pass
        return
    if fsize > Config.TG_MAX_SIZE:
        LOGGER.warning(
            "Skipping oversized upload for %s: %s bytes exceeds %s bytes",
            doc_f,
            fsize,
            Config.TG_MAX_SIZE,
        )
        try:
            await unzipperbot.send_message(
                c_id,
                Messages.TOO_LARGE,
                disable_notification=True,
            )
        except:
            pass
        return

    upmsg = None
    max_retries = 3
    for attempt in range(max_retries):
        try:
            ul_mode = await get_upload_mode(c_id)
            fname = os.sep.join(os.path.abspath(doc_f).split(os.sep)[5:])
            fext = (pathlib.Path(os.path.abspath(doc_f)).suffix).casefold().replace(".", "")
            thumbornot = await thumb_exists(c_id)
            thumb_image = (
                Config.THUMB_LOCATION + "/" + str(c_id) + ".jpg" if thumbornot else None
            )
            upmsg = await unzipperbot.send_message(
                c_id, Messages.PROCESSING2, disable_notification=True
            )
            progress_args = (
                Messages.TRY_UP.format(fname),
                upmsg,
                time(),
                unzip_bot,
            )

            uploaded = False

            # Try uploading as media first, fallback to document
            if ul_mode == "media" and fext in extentions_list["audio"]:
                try:
                    metadata = await get_audio_metadata(doc_f)
                    await unzip_bot.send_audio(
                        chat_id=c_id,
                        audio=doc_f,
                        caption=Messages.EXT_CAPTION.format(fname),
                        duration=metadata["duration"],
                        performer=metadata["performer"],
                        title=metadata["title"],
                        thumb=thumb_image,
                        disable_notification=True,
                        progress=progress_for_pyrogram,
                        progress_args=progress_args,
                    )
                    uploaded = True
                except (FloodWait, FileNotFoundError):
                    raise  # Let the outer handler deal with these
                except Exception as e:
                    LOGGER.warning(f"Audio upload failed for {doc_f}, falling back to document: {e}")

            elif ul_mode == "media" and fext in extentions_list["photo"]:
                try:
                    await unzip_bot.send_photo(
                        chat_id=c_id,
                        photo=doc_f,
                        caption=Messages.EXT_CAPTION.format(fname),
                        disable_notification=True,
                        progress=progress_for_pyrogram,
                        progress_args=progress_args,
                    )
                    uploaded = True
                except (FloodWait, FileNotFoundError):
                    raise
                except Exception as e:
                    LOGGER.warning(f"Photo upload failed for {doc_f}, falling back to document: {e}")

            elif ul_mode == "media" and fext in extentions_list["video"]:
                try:
                    vid_duration = await run_shell_cmds(
                        f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{doc_f}"'
                    )
                    try:
                        duration = int(float(vid_duration))
                    except (ValueError, TypeError):
                        duration = 0

                    # Generate thumbnail if user doesn't have a custom one
                    vid_thumb = thumb_image
                    if not vid_thumb:
                        thmb_pth = f"{Config.THUMB_LOCATION}/thumbnail_{os.path.basename(doc_f)}.jpg"
                        try:
                            if os.path.exists(thmb_pth):
                                os.remove(thmb_pth)
                            if duration > 0:
                                midpoint = duration // 2
                                await run_shell_cmds(
                                    f'ffmpeg -ss {midpoint} -i "{doc_f}" -vf "scale=320:320:force_original_aspect_ratio=decrease" -frames:v 1 -update 1 "{thmb_pth}"'
                                )
                            # Validate the thumbnail is real (not empty/corrupted)
                            if os.path.exists(thmb_pth) and os.path.getsize(thmb_pth) > 0:
                                vid_thumb = thmb_pth
                            else:
                                vid_thumb = str(Config.BOT_THUMB)
                        except Exception:
                            vid_thumb = str(Config.BOT_THUMB)

                    await unzip_bot.send_video(
                        chat_id=c_id,
                        video=doc_f,
                        caption=Messages.EXT_CAPTION.format(fname),
                        duration=duration,
                        thumb=vid_thumb,
                        disable_notification=True,
                        progress=progress_for_pyrogram,
                        progress_args=progress_args,
                    )
                    uploaded = True

                    # Clean up generated thumbnail
                    if vid_thumb and vid_thumb != thumb_image and vid_thumb != str(Config.BOT_THUMB):
                        try:
                            os.remove(vid_thumb)
                        except:
                            pass
                except (FloodWait, FileNotFoundError):
                    raise
                except Exception as e:
                    LOGGER.warning(f"Video upload failed for {doc_f}, falling back to document: {e}")

            # Fallback: send as document (also used for non-media mode)
            if not uploaded:
                try:
                    # Try without thumbnail first — thumb can cause MEDIA_FILE_INVALID
                    await unzip_bot.send_document(
                        chat_id=c_id,
                        document=doc_f,
                        caption=Messages.EXT_CAPTION.format(fname),
                        disable_notification=True,
                        progress=progress_for_pyrogram,
                        progress_args=progress_args,
                    )
                except (FloodWait, FileNotFoundError):
                    raise
                except Exception as e:
                    LOGGER.warning(f"Document upload also failed for {doc_f}: {e}")
                    error_str = str(e)
                    if "MEDIA_FILE_INVALID" not in error_str:
                        raise  # Let the outer handler deal with it
                    zipped_doc = f"{doc_f}.upload.zip"
                    try:
                        await asyncio.to_thread(_zip_for_upload, doc_f, zipped_doc)
                        zipped_size = await get_size(zipped_doc)
                        if zipped_size in (-1, 0) or zipped_size > Config.TG_MAX_SIZE:
                            raise e
                        await unzip_bot.send_document(
                            chat_id=c_id,
                            document=zipped_doc,
                            caption=Messages.EXT_CAPTION.format(fname + ".zip"),
                            disable_notification=True,
                            progress=progress_for_pyrogram,
                            progress_args=progress_args,
                        )
                    finally:
                        try:
                            os.remove(zipped_doc)
                        except:
                            pass

            # Upload succeeded — clean up progress message and file
            try:
                await upmsg.delete()
            except:
                pass
            try:
                os.remove(doc_f)
            except:
                pass
            # Small delay to avoid triggering FloodWait on next file
            await asyncio.sleep(1)
            return  # Success, exit the retry loop

        except FloodWait as f:
            LOGGER.warning(f"FloodWait for {f.value}s on attempt {attempt + 1} uploading {doc_f}")
            if upmsg:
                try:
                    await upmsg.delete()
                except:
                    pass
                upmsg = None
            await asyncio.sleep(f.value)
            continue  # Retry with the loop
        except FileNotFoundError:
            if upmsg:
                try:
                    await upmsg.delete()
                except:
                    pass
            try:
                await unzipperbot.send_message(
                    c_id, Messages.CANT_FIND.format(os.path.basename(doc_f))
                )
            except:
                pass
            return
        except BaseException as e:
            error_str = str(e)
            is_permanent = "400" in error_str or "INVALID" in error_str or "BAD_REQUEST" in error_str
            LOGGER.error(f"send_file failed for {doc_f} (attempt {attempt + 1}, permanent={is_permanent}): {e}")
            if upmsg:
                try:
                    await upmsg.delete()
                except:
                    pass
                upmsg = None
            # Don't retry permanent errors (400 Bad Request) — same file will always fail
            if not is_permanent and attempt < max_retries - 1:
                await asyncio.sleep(2)
                continue  # Retry only transient errors
            # Permanent error or final attempt — notify user, don't waste more bandwidth
            try:
                await unzipperbot.send_message(
                    c_id,
                    f"❌ **Upload failed** for `{os.path.basename(doc_f)}`\n\nError: `{e}`",
                )
            except:
                pass
            return


async def forward_file(message, cid):
    try:
        await unzipperbot.copy_message(
            chat_id=cid,
            from_chat_id=message.chat.id,
            message_id=message.id,
            disable_notification=True,
        )
    except FloodWait as f:
        await asyncio.sleep(f.value)
        return await forward_file(message, cid)


async def send_url_logs(unzip_bot, c_id, doc_f, source, message):
    try:
        u_file_size = os.stat(doc_f).st_size
        if Config.TG_MAX_SIZE < int(u_file_size):
            await unzip_bot.send_message(chat_id=c_id, text=Messages.TOO_LARGE)
            return
        fname = os.path.basename(doc_f)
        await unzip_bot.send_document(
            chat_id=c_id,
            document=doc_f,
            caption=Messages.LOG_CAPTION.format(fname, source),
            disable_notification=True,
            progress=progress_urls,
            progress_args=(
                Messages.CHECK_MSG,
                message,
                time(),
            ),
        )
    except FloodWait as f:
        await asyncio.sleep(f.value)
        return send_url_logs(unzip_bot, c_id, doc_f, source, message)
    except FileNotFoundError:
        await unzip_bot.send_message(
            chat_id=Config.LOGS_CHANNEL,
            text=Messages.ARCHIVE_GONE,
        )
    except BaseException:
        pass


async def merge_splitted_archives(user_id, path):
    cmd = f'cd "{path}" && cat * > MERGED_{user_id}.zip'
    await run_shell_cmds(cmd)


# Function to remove basic markdown characters from a string
async def rm_mark_chars(text: str):
    return re.sub("[*`_]", "", text)


# Function to answer queries
async def answer_query(
    query, message_text: str, answer_only: bool = False, unzip_client=None, buttons=None
):
    try:
        if answer_only:
            await query.answer(await rm_mark_chars(message_text), show_alert=True)
        else:
            await query.message.edit(message_text, reply_markup=buttons)
    except:
        try:
            if unzip_client:
                await unzip_client.send_message(
                    chat_id=query.message.chat.id,
                    text=message_text,
                    reply_markup=buttons,
                )
            else:
                await unzipperbot.send_message(
                    chat_id=query.message.chat.id,
                    text=message_text,
                    reply_markup=buttons,
                )
        except:
            pass
