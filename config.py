# Copyright (c) 2022 - 2024 UnxTar
import os


class Config:
    APP_ID = int(os.environ.get("APP_ID"))
    API_HASH = os.environ.get("API_HASH")
    BOT_TOKEN = os.environ.get("BOT_TOKEN")
    LOGS_CHANNEL = (
        int(os.environ.get("LOGS_CHANNEL"))
        if os.environ.get("LOGS_CHANNEL").strip("-").isdigit()
        else os.environ.get("LOGS_CHANNEL")
    )
    MONGODB_URL = os.environ.get("MONGODB_URL")
    MONGODB_DBNAME = os.environ.get("MONGODB_DBNAME", "Unzipper_Bot")
    BOT_OWNER = int(os.environ.get("BOT_OWNER"))
    DOWNLOAD_LOCATION = f"{os.path.dirname(__file__)}/Downloaded"
    THUMB_LOCATION = f"{os.path.dirname(__file__)}/Thumbnails"
    # Keep upload parts below Telegram's practical bot upload ceiling.
    TG_MAX_SIZE = int(os.environ.get("TG_MAX_SIZE", int(1.5 * 1024 * 1024 * 1024)))
    MAX_MESSAGE_LENGTH = 4096
    # URL download tuning. Telegram downloads use MAX_CONCURRENT_TRANSMISSIONS.
    CHUNK_SIZE = int(os.environ.get("CHUNK_SIZE", 1024 * 1024 * 16))  # 16 MB
    DOWNLOAD_READ_BUFFER_SIZE = int(
        os.environ.get("DOWNLOAD_READ_BUFFER_SIZE", 1024 * 1024 * 4)
    )  # 4 MB
    DOWNLOAD_PROGRESS_INTERVAL = int(os.environ.get("DOWNLOAD_PROGRESS_INTERVAL", 5))
    MAX_CONCURRENT_TRANSMISSIONS = int(
        os.environ.get("MAX_CONCURRENT_TRANSMISSIONS", 20)
    )
    BOT_THUMB = f"{os.path.dirname(__file__)}/bot_thumb.jpg"
    MAX_CONCURRENT_TASKS = 75
    MAX_TASK_DURATION_EXTRACT = 120 * 60  # 2 hours (in seconds)
    MAX_TASK_DURATION_MERGE = 240 * 60  # 4 hours (in seconds)
