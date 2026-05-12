# Copyright (c) 2022 - 2024 UnxTar
import asyncio
import json
import os
import re
import shutil


from aiofiles import open as openfile
from aiohttp import ClientSession, ClientTimeout, InvalidURL, TCPConnector
from email.parser import Parser
from email.policy import default
from fnmatch import fnmatch
from pyrogram import Client
from pyrogram.errors import ReplyMarkupTooLong
from pyrogram.types import CallbackQuery
from time import time
from urllib.parse import unquote

from .bot_data import Buttons, ERROR_MSGS, Messages
from .commands import get_stats, https_url_regex, sufficient_disk_space
from .ext_script.ext_helper import (
    _test_with_7z_helper,
    extr_files,
    get_files,
    make_keyboard,
    make_keyboard_empty,
    split_files,
)
from .ext_script.up_helper import answer_query, get_size, send_file, send_url_logs
from config import Config
from unzipper import LOGGER, unzipperbot
from unzipper.helpers.database import (
    add_cancel_task,
    add_ongoing_task,
    count_ongoing_tasks,
    del_cancel_task,
    del_ongoing_task,
    get_cancel_task,
    get_maintenance,
    get_ongoing_tasks,
    set_upload_mode,
    update_uploaded,
)
from unzipper.helpers.unzip_help import (
    TransferCancelled,
    extentions_list,
    humanbytes,
    progress_for_pyrogram,
    TimeFormatter,
    edit_ui_message,
)

split_file_pattern = r"\.(?:z\d+|r\d{2})$"
rar_file_pattern = r"\.part\d+\.rar$"
telegram_url_pattern = r"(?:http[s]?:\/\/)?(?:www\.)?t\.me\/([a-zA-Z0-9_]+)\/(\d+)"


def get_download_session():
    return ClientSession(
        connector=TCPConnector(limit=0, ttl_dns_cache=300),
        read_bufsize=Config.DOWNLOAD_READ_BUFFER_SIZE,
        timeout=ClientTimeout(total=None, sock_connect=60, sock_read=None),
    )


async def download(url, path):
    try:
        async with get_download_session() as session, session.get(
            url, allow_redirects=True
        ) as resp, openfile(path, mode="wb") as file:
            async for chunk in resp.content.iter_chunked(Config.CHUNK_SIZE):
                await file.write(chunk)
    except InvalidURL:
        LOGGER.error(Messages.INVALID_URL)
    except Exception:
        LOGGER.error(Messages.ERR_DL.format(url))


async def download_with_progress(url, path, message, unzip_bot):
    try:
        async with get_download_session() as session, session.get(
            url, allow_redirects=True
        ) as resp:
            total_size = int(resp.headers.get("Content-Length", 0))
            current_size = 0
            start_time = time()
            last_cancel_check = start_time
            last_progress_update = start_time

            async with openfile(path, mode="wb") as file:
                async for chunk in resp.content.iter_chunked(Config.CHUNK_SIZE):
                    # Throttle cancel-check to once per 5 seconds
                    now = time()
                    if message.from_user is not None and (now - last_cancel_check) >= 5:
                        last_cancel_check = now
                        if await get_cancel_task(message.from_user.id):
                            await edit_ui_message(message, text=Messages.DL_STOPPED)
                            await del_cancel_task(message.from_user.id)
                            return False

                    await file.write(chunk)
                    current_size += len(chunk)
                    if (
                        current_size == total_size
                        or now - last_progress_update
                        >= Config.DOWNLOAD_PROGRESS_INTERVAL
                    ):
                        last_progress_update = now
                        await progress_for_pyrogram(
                            current_size,
                            total_size,
                            Messages.DL_URL.format(url),
                            message,
                            start_time,
                            unzip_bot,
                        )

    except TransferCancelled:
        return False
    except Exception:
        LOGGER.error(Messages.ERR_DL.format(url))




async def async_generator(iterable):
    for item in iterable:
        yield item


def log_task_event(event, **fields):
    LOGGER.info(json.dumps({"event": event, **fields}, default=str))


async def wait_for_task_slot(unzip_bot, user_id):
    if user_id == Config.BOT_OWNER:
        return True
    ogtasks = await get_ongoing_tasks()
    if len(ogtasks) < Config.MAX_CONCURRENT_TASKS or any(
        task.get("user_id") == user_id for task in ogtasks
    ):
        return True

    notice = await unzip_bot.send_message(
        chat_id=user_id,
        text=(
            "All workers are busy. Your request is queued and will start "
            "when a slot opens."
        ),
    )
    waited = 0
    while waited < Config.TASK_QUEUE_WAIT_TIMEOUT:
        await asyncio.sleep(Config.TASK_QUEUE_POLL_INTERVAL)
        waited += Config.TASK_QUEUE_POLL_INTERVAL
        ogtasks = await get_ongoing_tasks()
        if len(ogtasks) < Config.MAX_CONCURRENT_TASKS or any(
            task.get("user_id") == user_id for task in ogtasks
        ):
            try:
                await notice.edit("A worker slot is free now. Starting your task...")
            except:
                pass
            return True
        if waited % 60 == 0:
            try:
                await notice.edit(
                    "Still queued. I will keep checking for a free worker slot."
                )
            except:
                pass

    try:
        await notice.edit(
            "The queue wait timed out. Please try again in a little while."
        )
    except:
        pass
    return False


async def upload_all_extracted_files(
    unzip_bot, query, user_id, chat_id, download_id, file_path, log_msg
):
    paths = await get_files(path=file_path)
    log_task_event(
        "upload_all_started",
        user_id=user_id,
        chat_id=chat_id,
        file_count=len(paths),
        path=file_path,
    )
    LOGGER.info("upload_all paths : " + str(paths))
    if not paths:
        try:
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{download_id}")
        except:
            pass
        await del_ongoing_task(user_id)
        await edit_ui_message(query.message, text=Messages.NO_FILE_LEFT, reply_markup=Buttons.RATE_ME)
        return

    sent_files = 0
    failed_files = []
    await edit_ui_message(query.message, Messages.SEND_ALL_FILES)
    async_paths = async_generator(paths)
    async for file in async_paths:
        fsize = await get_size(file)
        if fsize <= Config.TG_MAX_SIZE:
            status = await send_file(
                unzip_bot=unzip_bot,
                c_id=chat_id,
                doc_f=file,
                query=query,
                full_path=f"{Config.DOWNLOAD_LOCATION}/{download_id}",
                log_msg=log_msg,
                split=False,
            )
            if status == "success":
                sent_files += 1
            elif status == "cancelled":
                await del_ongoing_task(user_id)
                return
            else:
                failed_files.append(file)
            log_task_event(
                "upload_file_finished",
                user_id=user_id,
                file=file,
                status=status,
            )
            continue

        fname = file.split("/")[-1]
        smessage = await unzip_bot.send_message(
            chat_id=user_id, text=Messages.SPLITTING.format(fname)
        )
        splitteddir = f"{Config.DOWNLOAD_LOCATION}/splitted/{user_id}"
        os.makedirs(splitteddir, exist_ok=True)
        ooutput = f"{splitteddir}/{fname}"
        splittedfiles = await split_files(file, ooutput, Config.TG_MAX_SIZE)
        LOGGER.info(splittedfiles)
        if not splittedfiles:
            try:
                shutil.rmtree(splitteddir)
            except:
                pass
            await del_ongoing_task(user_id)
            await edit_ui_message(smessage, Messages.ERR_SPLIT)
            return
        await edit_ui_message(smessage, Messages.SEND_ALL_PARTS.format(fname))
        async_splittedfiles = async_generator(splittedfiles)
        async for s_file in async_splittedfiles:
            status = await send_file(
                unzip_bot=unzip_bot,
                c_id=chat_id,
                doc_f=s_file,
                query=query,
                full_path=splitteddir,
                log_msg=log_msg,
                split=True,
            )
            if status == "success":
                sent_files += 1
            elif status == "cancelled":
                await del_ongoing_task(user_id)
                return
            else:
                failed_files.append(file)
            log_task_event(
                "upload_part_finished",
                user_id=user_id,
                file=s_file,
                status=status,
            )
        try:
            shutil.rmtree(splitteddir)
        except:
            pass
        try:
            await smessage.delete()
        except:
            pass

    try:
        await log_msg.reply(Messages.HOW_MANY_UPLOADED.format(sent_files))
    except Exception as e:
        LOGGER.warning("Failed to write upload count log for %s: %s", user_id, e)
    await update_uploaded(user_id, upload_count=sent_files)
    await del_ongoing_task(user_id)
    if failed_files:
        log_task_event(
            "upload_all_finished",
            user_id=user_id,
            sent_files=sent_files,
            failed_files=len(failed_files),
            status="partial_failure",
        )
        failed_names = "\n".join(f"- `{os.path.basename(file)}`" for file in failed_files[:10])
        if len(failed_files) > 10:
            failed_names += f"\n...and {len(failed_files) - 10} more"
        fail_text = (
            f"⚠️ Uploaded {sent_files} file(s), but {len(failed_files)} failed.\n"
            f"The failed files were kept on disk for retry:\n{failed_names}"
        )
        await edit_ui_message(query.message, fail_text)
        try:
            await log_msg.reply(fail_text)
        except Exception as e:
            LOGGER.warning("Failed to write upload failure log for %s: %s", user_id, e)
        return
    try:
        await unzip_bot.send_message(
            chat_id=user_id, text=Messages.UPLOADED, reply_markup=Buttons.RATE_ME
        )
        await edit_ui_message(query.message, text=Messages.UPLOADED, reply_markup=Buttons.RATE_ME)
    except:
        pass
    log_task_event(
        "upload_all_finished",
        user_id=user_id,
        sent_files=sent_files,
        failed_files=0,
        status="success",
    )
    try:
        shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{download_id}")
    except Exception as e:
        await edit_ui_message(query.message, Messages.ERROR_TXT.format(e))
        LOGGER.error(e)


# Callbacks
@unzipperbot.on_callback_query()
async def unzipper_cb(unzip_bot: Client, query: CallbackQuery):
    uid = query.from_user.id
    if not await wait_for_task_slot(unzip_bot, uid):
        return

    if uid != Config.BOT_OWNER and await get_maintenance():
        await answer_query(query, Messages.MAINTENANCE_ON)
        return

    sent_files = 0
    global log_msg

    if query.data == "megoinhome":
        await edit_ui_message(
            query.message,
            text=Messages.START_TEXT.format(query.from_user.mention),
            reply_markup=Buttons.START_BUTTON,
        )

    elif query.data == "helpcallback":
        await edit_ui_message(
            query.message,
            text=Messages.HELP_TXT, reply_markup=Buttons.ME_GOIN_HOME
        )

    elif query.data == "aboutcallback":
        await edit_ui_message(
            query.message,
            text=Messages.ABOUT_TXT,
            reply_markup=Buttons.ME_GOIN_HOME
        )

    elif query.data == "donatecallback":
        await edit_ui_message(
            query.message,
            text=Messages.DONATE_TEXT,
            reply_markup=Buttons.ME_GOIN_HOME
        )

    elif query.data.startswith("statscallback"):
        if query.data.endswith("refresh"):
            await edit_ui_message(query.message, text=Messages.REFRESH_STATS)
        text_stats = await get_stats(query.from_user.id)
        await edit_ui_message(
            query.message,
            text=text_stats,
            reply_markup=Buttons.REFRESH_BUTTON,
        )

    elif query.data == "canceldownload":
        await add_cancel_task(query.from_user.id)



    elif query.data.startswith("extract_file"):
        user_id = query.from_user.id
        start_time = time()
        await add_ongoing_task(user_id, start_time, "extract")
        log_task_event("task_started", user_id=user_id, task_type="extract")
        download_path = f"{Config.DOWNLOAD_LOCATION}/{user_id}"
        ext_files_dir = f"{download_path}/extracted"
        r_message = query.message.reply_to_message
        splitted_data = query.data.split("|")
        try:
            await edit_ui_message(query.message, Messages.PROCESSING_TASK)
        except:
            pass
        log_msg = await unzip_bot.send_message(
            chat_id=Config.LOGS_CHANNEL, text=Messages.USER_QUERY.format(user_id)
        )
        global archive_msg

        try:
            if splitted_data[1] == "url":
                url = r_message.text
                # Double check
                if not re.match(https_url_regex, url):
                    await del_ongoing_task(user_id)
                    await edit_ui_message(query.message, Messages.INVALID_URL)
                    return
                if re.match(telegram_url_pattern, url):
                    r_message = await unzip_bot.get_messages(
                        chat_id=url.split("/")[-2], message_ids=int(url.split("/")[-1])
                    )
                    splitted_data[1] = "tg_file"
                if splitted_data[1] == "url":
                    s = get_download_session()
                    async with s as session:
                        # Get the file size
                        unzip_head = await session.head(url, allow_redirects=True)
                        metadata_headers = unzip_head.headers
                        metadata_status = unzip_head.status
                        f_size = metadata_headers.get("content-length")
                        u_file_size = f_size if f_size else "undefined"
                        if u_file_size != "undefined" and not sufficient_disk_space(
                            int(u_file_size)
                        ):
                            await del_ongoing_task(user_id)
                            await edit_ui_message(query.message, Messages.NO_SPACE)
                            return
                        await edit_ui_message(log_msg, 
                            Messages.LOG_TXT.format(user_id, url, u_file_size)
                        )
                        archive_msg = log_msg
                        content_type = metadata_headers.get("content-type", "")
                        if not content_type or metadata_status != 200:
                            async with session.get(
                                url,
                                headers={"Range": "bytes=0-0"},
                                allow_redirects=True,
                            ) as probe_resp:
                                metadata_headers = probe_resp.headers
                                metadata_status = probe_resp.status
                                content_type = probe_resp.headers.get(
                                    "content-type", ""
                                )
                        if "application/" not in content_type:
                            await del_ongoing_task(user_id)
                            await edit_ui_message(query.message, Messages.NOT_AN_ARCHIVE)
                            return
                        content_disposition = metadata_headers.get(
                            "content-disposition"
                        )
                        rfnamebro = ""
                        real_filename = ""
                        if content_disposition:
                            headers = Parser(policy=default).parsestr(
                                f"Content-Disposition: {content_disposition}"
                            )
                            real_filename = headers.get_filename()
                            if real_filename != "":
                                rfnamebro = unquote(real_filename)
                        if rfnamebro == "":
                            rfnamebro = unquote(url.split("/")[-1])
                        if metadata_status in (200, 206):
                            os.makedirs(download_path, exist_ok=True)
                            s_time = time()
                            if real_filename:
                                archive = os.path.join(download_path, real_filename)
                                fext = real_filename.split(".")[-1].casefold()
                            else:
                                fname = unquote(os.path.splitext(url)[1])
                                fname = fname.split("?")[0]
                                fext = fname.split(".")[-1].casefold()
                                archive = f"{download_path}/{fname}"
                            if (
                                splitted_data[2] not in ["thumb", "thumbrename"]
                                and fext not in extentions_list["archive"]
                            ):
                                await del_ongoing_task(user_id)
                                await edit_ui_message(query.message, Messages.DEF_NOT_AN_ARCHIVE)
                                try:
                                    shutil.rmtree(
                                        f"{Config.DOWNLOAD_LOCATION}/{user_id}"
                                    )
                                except:
                                    pass
                                return
                            await answer_query(
                                query, Messages.PROCESSING2, unzip_client=unzip_bot
                            )
                            try:
                                dled = await download_with_progress(
                                    url, archive, query.message, unzip_bot
                                )
                            except Exception as e:
                                dled = False
                                LOGGER.error(Messages.ERR_DL.format(e))
                            if isinstance(dled, bool) and not dled:
                                return
                            e_time = time()
                            await send_url_logs(
                                unzip_bot=unzip_bot,
                                c_id=Config.LOGS_CHANNEL,
                                doc_f=archive,
                                source=url,
                                message=query.message,
                            )
                        else:
                            await del_ongoing_task(user_id)
                            await edit_ui_message(query.message, Messages.CANT_DL_URL)
                            try:
                                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{user_id}")
                            except:
                                pass
                            return

            elif splitted_data[1] == "tg_file":
                if r_message.document is None:
                    await del_ongoing_task(user_id)
                    await edit_ui_message(query.message, Messages.GIVE_ARCHIVE)
                    return
                fname = r_message.document.file_name
                rfnamebro = fname
                archive_msg = await r_message.forward(chat_id=Config.LOGS_CHANNEL)
                await edit_ui_message(log_msg, 
                    Messages.LOG_TXT.format(
                        user_id, fname, humanbytes(r_message.document.file_size)
                    )
                )
                if splitted_data[2] not in ["thumb", "thumbrename"]:
                    fext = fname.split(".")[-1].casefold()
                    if (
                        fnmatch(fext, extentions_list["split"][0])
                        or fext in extentions_list["split"]
                        or bool(re.search(rar_file_pattern, fname))
                    ):
                        await edit_ui_message(query.message, Messages.ITS_SPLITTED)
                        return

                os.makedirs(download_path, exist_ok=True)
                s_time = time()
                location = f"{download_path}/{fname}"
                LOGGER.info("location: %s", location)
                archive = await r_message.download(
                    file_name=location,
                    progress=progress_for_pyrogram,
                    progress_args=(
                        Messages.TRY_DL,
                        query.message,
                        s_time,
                        unzip_bot,
                    ),
                )
                e_time = time()
            else:
                await del_ongoing_task(user_id)
                await answer_query(
                    query,
                    Messages.QUERY_PARSE_ERR,
                    answer_only=True,
                    unzip_client=unzip_bot,
                )
                return



            dltime = TimeFormatter(round(e_time - s_time) * 1000)
            if dltime == "":
                dltime = "1s"
            await answer_query(
                query, Messages.AFTER_OK_DL_TXT.format(dltime), unzip_client=unzip_bot
            )

            # Attempt to fetch password protected archives
            if splitted_data[2] == "with_pass":
                password = await unzip_bot.ask(
                    chat_id=query.message.chat.id, text=Messages.PLS_SEND_PASSWORD
                )
                ext_s_time = time()
                extractor = await extr_files(
                    path=ext_files_dir,
                    archive_path=archive,
                    password=password.text,
                )
                ext_e_time = time()
                await archive_msg.reply(Messages.PASS_TXT.format(password.text))
            else:
                ext_s_time = time()
                tested = await _test_with_7z_helper(archive)
                ext_t_time = time()
                testtime = TimeFormatter(round(ext_t_time - ext_s_time) * 1000)
                if testtime == "":
                    testtime = "1s"
                await answer_query(
                    query,
                    Messages.AFTER_OK_TEST_TXT.format(testtime),
                    unzip_client=unzip_bot,
                )
                if tested:
                    extractor = await extr_files(
                        path=ext_files_dir, archive_path=archive
                    )
                    ext_e_time = time()
                else:
                    LOGGER.info("Error on test")
                    extractor = "Error"
                    ext_e_time = time()
            # Checks if there is an error happened while extracting the archive
            if any(err in extractor for err in ERROR_MSGS):
                try:
                    await edit_ui_message(query.message, Messages.EXT_FAILED_TXT)
                    shutil.rmtree(ext_files_dir)
                    await del_ongoing_task(user_id)
                    await log_msg.reply(Messages.EXT_FAILED_TXT)
                    return
                except:
                    try:
                        await query.message.delete()
                    except:
                        pass
                    await unzip_bot.send_message(
                        chat_id=query.message.chat.id, text=Messages.EXT_FAILED_TXT
                    )
                    shutil.rmtree(ext_files_dir)
                    await del_ongoing_task(user_id)
                    await archive_msg.reply(Messages.EXT_FAILED_TXT)
                    return
            # Check if user was dumb 😐
            paths = await get_files(path=ext_files_dir)
            if not paths:
                await archive_msg.reply(Messages.PASSWORD_PROTECTED)
                await unzip_bot.send_message(
                    chat_id=query.message.chat.id,
                    text=Messages.PASSWORD_PROTECTED,
                )
                await answer_query(
                    query, Messages.EXT_FAILED_TXT, unzip_client=unzip_bot
                )
                shutil.rmtree(ext_files_dir)
                await del_ongoing_task(user_id)
                return

            # Upload extracted files
            extrtime = TimeFormatter(round(ext_e_time - ext_s_time) * 1000)
            if extrtime == "":
                extrtime = "1s"
            await answer_query(
                query, Messages.EXT_OK_TXT.format(extrtime), unzip_client=unzip_bot
            )

            await upload_all_extracted_files(
                unzip_bot=unzip_bot,
                query=query,
                user_id=user_id,
                chat_id=query.message.chat.id,
                download_id=user_id,
                file_path=ext_files_dir,
                log_msg=log_msg,
            )

        except Exception as e:
            await del_ongoing_task(user_id)
            try:
                try:
                    await edit_ui_message(query.message, Messages.ERROR_TXT.format(e))
                except:
                    await unzip_bot.send_message(
                        chat_id=query.message.chat.id, text=Messages.ERROR_TXT.format(e)
                    )
                await archive_msg.reply(Messages.ERROR_TXT.format(e))
                shutil.rmtree(ext_files_dir)
                try:
                    await ClientSession().close()
                except:
                    pass
                LOGGER.error(e)
            except Exception as err:
                LOGGER.error(err)
                await archive_msg.reply(err)

    elif query.data.startswith("ext_f"):
        LOGGER.info(query.data)
        user_id = query.from_user.id
        spl_data = query.data.split("|")
        file_path = f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}/extracted"

        try:
            urled = spl_data[4] if isinstance(spl_data[4], bool) else False
        except:
            urled = False
        if urled:
            paths = spl_data[5].namelist()
        else:
            paths = await get_files(path=file_path)
        if not paths and not urled:
            if os.path.isdir(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}"):
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
            await del_ongoing_task(user_id)
            await edit_ui_message(query.message, 
                text=Messages.NO_FILE_LEFT, reply_markup=Buttons.RATE_ME
            )
            return
        LOGGER.info("ext_f paths : " + str(paths))
        try:
            await query.answer(Messages.SENDING_FILE)
            await edit_ui_message(query.message, text=Messages.UPLOADING_THIS_FILE)
        except:
            pass
        sent_files += 1
        if urled:
            file = spl_data[5].open(paths[int(spl_data[3])])
        else:
            file = paths[int(spl_data[3])]
        fsize = await get_size(file)
        split = False
        if fsize <= Config.TG_MAX_SIZE:
            await send_file(
                unzip_bot=unzip_bot,
                c_id=spl_data[2],
                doc_f=file,
                query=query,
                full_path=f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}",
                log_msg=log_msg,
                split=False,
            )
        else:
            split = True
        if split:
            fname = file.split("/")[-1]
            smessage = await unzip_bot.send_message(
                chat_id=user_id, text=Messages.SPLITTING.format(fname)
            )
            splitteddir = f"{Config.DOWNLOAD_LOCATION}/splitted/{user_id}"
            os.makedirs(splitteddir, exist_ok=True)
            ooutput = f"{splitteddir}/{fname}"
            splittedfiles = await split_files(file, ooutput, Config.TG_MAX_SIZE)
            LOGGER.info(splittedfiles)
            if not splittedfiles:
                try:
                    shutil.rmtree(splitteddir)
                except:
                    pass
                await del_ongoing_task(user_id)
                await edit_ui_message(smessage, Messages.ERR_SPLIT)
                return
            await edit_ui_message(smessage, Messages.SEND_ALL_PARTS.format(fname))
            async_splittedfiles = async_generator(splittedfiles)
            async for s_file in async_splittedfiles:
                sent_files += 1
                await send_file(
                    unzip_bot=unzip_bot,
                    c_id=user_id,
                    doc_f=s_file,
                    query=query,
                    full_path=splitteddir,
                    log_msg=log_msg,
                    split=True,
                )
            try:
                shutil.rmtree(splitteddir)
            except:
                pass
            try:
                await smessage.delete()
            except:
                pass

        await edit_ui_message(query.message, Messages.REFRESHING)
        if urled:
            try:
                paths.pop(int(spl_data[3]))
            except:
                pass
            rpaths = paths
        else:
            try:
                os.remove(file)
            except:
                pass
            rpaths = await get_files(path=file_path)
        if not rpaths:
            try:
                shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}")
            except:
                pass
            await del_ongoing_task(user_id)
            await edit_ui_message(query.message, 
                text=Messages.NO_FILE_LEFT, reply_markup=Buttons.RATE_ME
            )
            return
        if urled:
            try:
                i_e_buttons = await make_keyboard(
                    paths=rpaths,
                    user_id=query.from_user.id,
                    chat_id=query.message.chat.id,
                    unziphttp=True,
                    rzfile=spl_data[5],
                )
                await edit_ui_message(query.message, 
                    Messages.SELECT_FILES, reply_markup=i_e_buttons
                )
            except ReplyMarkupTooLong:
                empty_buttons = await make_keyboard_empty(
                    user_id=user_id,
                    chat_id=query.message.chat.id,
                    unziphttp=True,
                    rzfile=spl_data[5],
                )
                await edit_ui_message(query.message, 
                    Messages.UNABLE_GATHER_FILES,
                    reply_markup=empty_buttons,
                )
        else:
            try:
                i_e_buttons = await make_keyboard(
                    paths=rpaths,
                    user_id=query.from_user.id,
                    chat_id=query.message.chat.id,
                    unziphttp=False,
                )
                await edit_ui_message(query.message, 
                    Messages.SELECT_FILES, reply_markup=i_e_buttons
                )
            except ReplyMarkupTooLong:
                empty_buttons = await make_keyboard_empty(
                    user_id=user_id, chat_id=query.message.chat.id, unziphttp=False
                )
                await edit_ui_message(query.message, 
                    Messages.UNABLE_GATHER_FILES,
                    reply_markup=empty_buttons,
                )
        await update_uploaded(user_id, upload_count=sent_files)

    elif query.data.startswith("ext_a"):
        LOGGER.info(query.data)
        user_id = query.from_user.id
        spl_data = query.data.split("|")
        file_path = f"{Config.DOWNLOAD_LOCATION}/{spl_data[1]}/extracted"
        await upload_all_extracted_files(
            unzip_bot=unzip_bot,
            query=query,
            user_id=user_id,
            chat_id=spl_data[2],
            download_id=spl_data[1],
            file_path=file_path,
            log_msg=log_msg,
        )
        return


    elif query.data == "cancel_dis":
        uid = query.from_user.id
        await del_ongoing_task(uid)
        try:
            await edit_ui_message(query.message, 
                Messages.CANCELLED_TXT.format(Messages.PROCESS_CANCELLED)
            )
            shutil.rmtree(f"{Config.DOWNLOAD_LOCATION}/{uid}")
            await update_uploaded(user_id=uid, upload_count=sent_files)
            try:
                await log_msg.reply(Messages.HOW_MANY_UPLOADED.format(sent_files))
            except:
                return
        except:
            await unzip_bot.send_message(
                chat_id=uid,
                text=Messages.CANCELLED_TXT.format(Messages.PROCESS_CANCELLED),
            )
            return

    elif query.data == "nobully":
        await edit_ui_message(query.message, Messages.CANCELLED)
