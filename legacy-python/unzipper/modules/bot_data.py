# Copyright (c) 2022 - 2024 UnxTar
from pyrogram.types import InlineKeyboardButton, InlineKeyboardMarkup


class Messages:
    # Buttons
    HELP = "ℹ️ Help"
    ABOUT = "📖 About"
    STATS_BTN = "📊 Stats"
    DONATE = "☕️ Donate"
    REFRESH = "🔄 Refresh"
    BACK = "⬅️ Back"
    CLEAN = "🧹 Clean Files"
    AS_DOC = "📄 Document"
    AS_MEDIA = "🎬 Media"
    MERGE_BTN = "🔄 Merge"
    CHECK = "👁️ View"
    REPLACE = "🔁 Replace"
    SAVE = "💾 Save"
    DELETE = "🗑️ Delete"
    RATE = "⭐️ Rate Us"

    # start.py
    PRIVATE_CHAT = "⚠️ **Error:** This command can only be used in a private chat."
    NO_LOG_ID = "⚠️ **Error:** No log channel ID has been provided."
    ERROR_LOG_CHECK = "❌ **Error:** Failed to check the log channel. Please ensure the LOGS_CHANNEL ID is correct."
    DL_THUMBS = "⏳ **Downloading {} thumbnails...**"
    DOWNLOADED_THUMBS = "✅ **Downloaded {} of {} thumbnails.**"
    BOT_RESTARTED = "\n🔄 **Bot Restarted**\n\n**Old boot time:** `{}`\n**New boot time:** `{}`\n    "
    RESEND_TASK = "\n⚠️ **Warning:** The bot restarted during your task.\nPlease resend it.\n    "
    TASK_EXPIRED = "\n⏱️ **Task Expired**\n\nYour task ran for over {} minutes and was terminated to save resources.\nPlease try again.\n    "

    # database.py
    BANNED = "\n🚫 **You are banned.**\n\nContact @UnxTar_chat if you believe this is a mistake.\n    "
    NEW_USER_BAD = "\n👤 **#NEW_USER**\n\n**Profile:** `{}`\n`[AttributeError]`\n    "
    NEW_USER = "\n👤 **#NEW_USER**\n\n**Profile:** `{}` {}\n**User ID:** `{}`\n**Profile URL:** [tg://user?id={}](tg://user?id={})\n    "

    # unzip_help.py
    UNKNOWN_SIZE = "\n**Size:** Unknown\n\n⏳ This might take a while...\n    "
    PROGRESS_MSG = "\n{}\n{}\n\n⚡️ **Powered by @UnxTarbots**\n    "
    PROCESSING = "⚙️ **Processing:**"
    SPEED = "🚀 **Speed:**"
    ETA = "⏱️ **ETA:**"

    # __main__.py
    START_TXT = "✅ Bot started successfully at `{}`."
    STOP_TXT = "💤 Bot is shutting down at `{}`."
    STARTING_BOT = "🚀 Starting bot..."
    CHECK_LOG = "🔍 Checking log channel..."
    LOG_CHECKED = "✅ Log channel verified."
    BOT_RUNNING = "🚀 Bot is now running! Join @UnxTarbots."
    WRONG_LOG = "\n❌ **Error:** The provided **LOGS_CHANNEL** (`{}`) is invalid.\nBot crashed.\n    "

    # callbacks.py
    MAX_TASKS = "\n⏳ **Server Busy**\n\nThe bot is currently at maximum capacity ({} tasks running).\nPlease try again in a few minutes.\n    "
    CHOOSE_EXT_MODE = "\n⚙️ **Select Extraction Mode** for {}:\n\n📁 : **Standard Mode**\n🔐 : **Password Protected**\n🖼️ : **Custom Thumbnail**\n✏️ : **Rename & Custom Thumbnail**\n❌ : **Cancel Task**\n    "
    CHOOSE_EXT_MODE_MERGE = "\n⚙️ **Select Extraction Mode** for merged file:\n\n📁 : **Standard Mode**\n🔐 : **Password Protected**\n❌ : **Cancel Task**\n    "
    EXT_CAPTION = "\n`{}`\n\n⚡️ Extracted by @unzip_UnxTarbot\n    "
    REPORT_TEXT = "\n📢 **#Report #Action_Required**\n\n**User:** `{}`\n**Message:** `{}`\n    "
    LOG_CAPTION = "\n📁 **File:** `{}`\n\n🔗 **Source URL:**\n`{}`\n    "
    EXT_FAILED_TXT = "\n❌ **Extraction Failed**\n\n**Troubleshooting:**\n• Ensure the archive is not corrupted.\n• Verify you selected the correct mode.\n• Check the password (case-sensitive).\n• The format might not be supported.\n\n⚠️ **Send /clean before trying another task.**\n\nReport persistent issues at @UnxTar_chat.\n    "
    HOW_MANY_UPLOADED = "✅ `{}` file(s) extracted successfully."
    PLS_REPLY = "⚠️ Please reply to an image to save it as a custom thumbnail."
    UPLOADING_THIS_FILE = "📤 Uploading file... Please wait."
    NO_MERGE_TASK = "\n⚠️ No active merge task found.\nUse **/merge** to start one.\n    "
    LOG_TXT = "\n📝 **Extraction Log**\n\n**User ID:** `{}`\n**File:** `{}`\n**Size:** `{}`\n    "
    PASS_TXT = "\n🔑 **Password:**\n`{}`\n    "
    DL_URL = "\n📥 **Downloading...**\n\n**URL:** `{}`\n    "
    REFRESH_STATS = "🔄 Refreshing stats..."
    ACTUAL_THUMB = "🖼️ Current Thumbnail"
    START_TEXT = "\n👋 Hi **{}**, welcome to **Unarchiver Bot**! 📦\n\nI can extract any archive (password protected, split, etc.).\nSend **/commands** to see what I can do.\n\n❤️ **Made by @UnxTarbots**\nConsider using **/donate** to support us!\n    "
    HELP_TXT = "\n**📖 How to use:**\n\n**1.** Send an archive file or URL.\n**2.** Choose the extraction mode.\n\n**Options:**\n• Change upload mode: **/mode**\n\n**Notes:**\n• Select 🔐 if the archive is password protected.\n• Use **/clean** if a task fails or hangs.\n• If the archive contains many files, select 'Upload all 📤'.\n\n💬 Need help? Join **@UnxTar_chat**\n    "
    ABOUT_TXT = "\n**ℹ️ About Unarchiver Bot [v6.3.5]**\n\n• **Language:** [Python 3.12.4](https://www.python.org/)\n• **Framework:** [Pyrogram 2.0.106](https://pyrogram.org/)\n• **Source code:** [UnxTar/unzip-bot](https://github.com/UnxTar/unzip-bot)\n• **Developer:** [UnxTar](https://github.com/UnxTar)\n\n⭐️ **[Rate Us](https://t.me/BotsArchive/2705)**\n❤️ Made by **@UnxTarbots**\n    "
    DONATE_TEXT = "\n**☕️ Support the Bot**\n\nKeeping this bot fast and free costs money. If you find it useful, please consider donating to help cover hosting and development costs.\n\n**Payment Options:**\n• **[PayPal](https://www.paypal.me/8UnxTar)**\n• **[GitHub Sponsors](https://github.com/sponsors/UnxTar)**\n• **[Telegram](https://t.me/UnxTarbots/698)**\n• **[BuyMeACoffee](https://www.buymeacoffee.com/UnxTar)**\n\nThank you for your support! ❤️\n    "
    VIP_INFO = "\n⏳ **VIP Subscriptions coming soon!**\n    "
    VIP_REQUIRED_MESSAGE = "Use this command as a reply to a messsage..."
    VIP_ADDED_USER = "The following user had been added..."
    CLEAN_TXT = "\n🧹 **Clean Tasks & Files?**\n\n⚠️ This will delete all your current pending tasks and downloaded files on the server.\n    "
    SELECT_UPLOAD_MODE_TXT = "\n⚙️ **Upload Mode**\n\nCurrent mode: `{}`\n    "
    CHANGED_UPLOAD_MODE_TXT = "✅ **Upload mode changed to:** `{}`"
    EXISTING_THUMB = "\n🖼️ **Custom Thumbnail exists.**\n\nWhat would you like to do?\n• View current thumbnail\n• Replace it\n• Cancel\n    "
    SAVING_THUMB = "💾 Save this image as your custom thumbnail?"
    SAVED_THUMBNAIL = "✅ **Thumbnail saved successfully.**"
    DEL_CONFIRM_THUMB = "\n🗑️ Are you sure you want to delete your custom thumbnail?\n• View current thumbnail\n• Delete it\n• Cancel\n    "
    DEL_CONFIRM_THUMB_2 = "🗑️ Confirm thumbnail deletion?"
    DELETED_THUMB = "✅ **Thumbnail deleted successfully.**"
    ERROR_THUMB_RENAME = "❌ Error renaming thumbnail."
    ERROR_THUMB_UPDATE = "❌ Error updating thumbnail in database."
    ERROR_TELEGRAPH_UPLOAD = "❌ Error uploading to Telegra.ph."
    ERROR_THUMB_DEL = "❌ Error deleting thumbnail: {}"
    AFTER_OK_DL_TXT = "\n✅ **Downloaded successfully**\n\n**Time:** `{}`\n**Status:** 🧪 Testing archive...\n    "
    AFTER_OK_MERGE_DL_TXT = "\n✅ **Downloaded {} files**\n\n**Time:** `{}`\n**Status:** 🔄 Merging archives...\n    "
    AFTER_OK_MERGE_TXT = "\n✅ **Merged successfully**\n\n**Time:** `{}`\n**Status:** ⚙️ Processing archive...\n    "
    AFTER_OK_TEST_TXT = "\n✅ **Test passed**\n\n**Time:** `{}`\n**Status:** 📦 Extracting...\n    "
    EXT_OK_TXT = "\n✅ **Extracted successfully**\n\n**Time:** `{}`\n**Status:** ⚙️ Processing files...\n    "
    ERROR_TXT = "\n❌ **Error occurred:**\n\n`{}`\n\nPlease report this at @UnxTar_chat if the issue persists.\n    "
    CANCELLED_TXT = "✅ **{}**"
    DL_STOPPED = "✅ **Download cancelled.**"
    PROCESSING_TASK = "⚙️ **Processing task... Please wait.**"
    ERROR_GET_MSG = "❌ Error retrieving messages: {}"
    PROCESS_MSGS = "⚙️ **Processing {} messages...**"
    DL_FILES = "\n📥 **Downloading file {}/{}...**\n\n    "
    PROCESS_MERGE = "\n📝 **Merge Task**\n\n**User ID:** {}\n**File:** {}\n    "
    PLS_SEND_PASSWORD = "🔑 **Please send the password:**"
    PASSWORD_PROTECTED = "🔒 Archive is password protected. Send **/clean** and try again using the 🔐 mode."
    SELECT_FILES = "📄 **Select files to upload:**"
    UNABLE_GATHER_FILES = "\n⚠️ **Unable to list files.**\nChoose 'Upload all' to send everything, or cancel.\n    "
    FATAL_ERROR = "❌ **Fatal Error:** Unrecognized archive format."
    USER_QUERY = "\n📝 **User Query**\n\n**User ID:** {}\n    "
    INVALID_URL = "❌ Invalid URL provided."
    NOT_AN_ARCHIVE = "\n❌ The downloaded file is not an archive.\n    "
    DEF_NOT_AN_ARCHIVE = "\n❌ This file is not an archive.\nIf you believe this is an error, send the file to **@UnxTar**\n    "
    PROCESSING2 = "⚙️ `Processing...`"
    UNZIP_HTTP = "❌ HTTP unzip error on {}: {}"
    ERR_DL = "❌ Download error: {}"
    CANT_DL_URL = "❌ **Cannot download from this URL.**"
    GIVE_ARCHIVE = "⚠️ Please provide an archive to extract."
    ITS_SPLITTED = "\n⚠️ This is a split archive part. Use the **/merge** command.\n    "
    SPL_RZ = "⚠️ Split RAR/ZIP files (.rxx, .zxx) are not supported yet."
    TRY_DL = "\n📥 **Downloading...**\n\n    "
    QUERY_PARSE_ERR = "\n❌ **Fatal Query Error**\nPlease contact @UnxTar_chat.\n    "
    GIVE_NEW_NAME = "\n✏️ **Rename File**\n\nCurrent name: `{}`\n\nSend the new name (**include extension!**):\n    "
    SPLITTING = "✂️ **Splitting `{}`...**"
    ERR_SPLIT = "❌ Error splitting file (exceeds 2GB)."
    SEND_ALL_PARTS = "📤 Uploading all parts of `{}`..."
    UPLOADED = "\n✅ **Upload complete!**\n\nJoin @UnxTarbots ❤️\n    "
    NO_FILE_LEFT = "⚠️ No files left to upload."
    SENDING_FILE = "📤 Uploading file..."
    SEND_ALL_FILES = "📤 Uploading all files..."
    REFRESHING = "🔄 Refreshing..."
    CANCELLED = "✅ **Cancelled successfully.**"
    PROCESS_CANCELLED = "Process cancelled"

    # commands.py
    PRIVACY = "🔒 **Privacy Policy**\n\nWe do not store your files. They are deleted immediately after processing."
    PROCESS_RUNNING = "\n⏳ You already have an active task.\nSend **/clean** to cancel it and start a new one.\n    "
    SPLIT_NOPE = "⚠️ This type of split archive is not supported."
    UNVALID = "⚠️ Please send a valid archive file or URL."
    NO_SPACE = "❌ **Storage Full:** Server is out of disk space."
    MERGE = "\n🔄 **Merge Archives**\n\nSend all split archive parts (.001, .002, etc.).\nOnce you have sent them all, send **/done**.\n    "
    DONE = "\n✅ **All parts sent?**\nClick the `Merge 🛠️` button below.\n    "
    STATS = "\n📊 **Bot Statistics**\n\n**💾 Storage:**\n• Total: `{}`\n• Used: `{} ({}%)`\n• Free: `{}`\n\n**⚙️ Processing:**\n• Active tasks: `{}`\n\n**🖥️ Hardware:**\n• CPU: `{}%`\n• RAM: `{}%`\n• Uptime: `{}`\n    "
    STATS_OWNER = "\n📊 **Admin Statistics**\n\n**👥 Users:**\n• Registered: `{}`\n• Banned: `{}`\n\n**💾 Storage:**\n• Total: `{}`\n• Used: `{} ({}%)`\n• Free: `{}`\n• Active tasks: `{}`\n\n**🌐 Network:**\n• Uploaded: `{}`\n• Downloaded: `{}`\n\n**🖥️ Hardware:**\n• CPU: `{}%`\n• RAM: `{}%`\n• Uptime: `{}`\n    "
    BC_REPLY = "📡 Reply to a message to broadcast it."
    BC_START = "\n📡 **Broadcasting...**\nUsers: {}/{}\n    "
    BC_DONE = "\n✅ **Broadcast Complete**\n\nTotal: `{}` | Success: `{}` | Failed: `{}`\n    "
    SEND_REPLY = "📡 Reply to a message to send it."
    PROVIDE_UID = "⚠️ Please provide a User ID."
    PROVIDE_UID2 = "⚠️ Please provide a User ID or Username."
    SENDING = "📤 Sending..."
    SEND_SUCCESS = "✅ Message sent to `{}`."
    SEND_FAILED = "\n❌ Failed to send to `{}`. They may have blocked the bot.\n    "
    REPORT_REPLY = "📢 Reply to a message to report it."
    REPORT_DONE = "\n✅ Report sent to admins.\n    "
    BAN_ID = "🚫 Provide a User ID to ban."
    ALREADY_BANNED = "\n⚠️ `{}` is already banned.\n    "
    ALREADY_REMOVED = "⚠️ `{}` is already removed from database."
    USER_BANNED = "\n🚫 **User Banned:**\n`{}`\n    "
    UNBAN_ID = "✅ Provide a User ID to unban."
    ALREADY_ADDED = "\n⚠️ `{}` is already in the database.\n    "
    ALREADY_UNBANNED = "⚠️ `{}` is not banned."
    UNBANNED = "\n✅ **User Unbanned:**\n`{}`\n    "
    INFO = "ℹ️ Send a forwarded message to get info."
    USER = "ℹ️ User stats module (WIP)."
    UNABLE_FETCH = "❌ Unable to fetch data."
    USER_INFO = "\n👤 **User ID:** `{}`\nFiles uploaded: `{}`\n    "
    UID_UNAME_INVALID = "❌ Invalid User ID or Username."
    USER2_INFO = "\n👤 **Info:**\n`{}`\n\n🔗 [Profile Link](tg://user?id={})\n    "
    MAINTENANCE = "\n🛠️ **Maintenance Mode**\nCurrent state: `{}`\nSend `True` or `False` to change.\n    "
    MAINTENANCE_ASK = "\nSend `True` to enable, `False` to disable.\n    "
    MAINTENANCE_DONE = "✅ Maintenance mode set to: `{}`"
    MAINTENANCE_ON = "\n🛠️ **Maintenance Mode is ON**\nThe bot is currently undergoing maintenance. Please check back later.\n    "
    MAINTENANCE_FAIL = "❌ Invalid input. Send `True` or `False`."
    NO_THUMBS = "⚠️ No thumbnails found."
    ERASE_ALL = "🧹 **Wiping all server files...**"
    CLEANED = "✅ **Server wiped completely.**"
    NOT_CLEANED = "❌ Error wiping server."
    ERASE_TASKS = "🧹 Deleting {} tasks..."
    ERASE_TASKS_SUCCESS = "✅ Deleted {} tasks."
    LOG_SENT = "📄 Log file sent to {}."
    DELETED_FOLDER = "🗑️ Deleted folder: {}"
    RESTARTED_AT = "🔄 **Bot restarted at:** `{}`"
    RESTARTING = "🔄 Restarting..."
    PULLING = "⬇️ Pulling updates from GitHub..."
    PULLED = "✅ Updates pulled. Restarting..."
    NO_PULL = "✅ Already up to date."
    COMMANDS_LIST = "\n**📋 Available Commands**\n\n**[File/URL]** : Extract the archive\n**/start** : Check bot status\n**/help** : Display help menu\n**/about** : About this bot\n**/donate** : Support the project\n**/clean** : Cancel tasks and clear files\n**/mode** : Set upload mode (Doc/Media)\n**/stats** : View bot statistics\n**/merge** : Start a merge task\n**/done** : Finish a merge task\n**/addthumb** : Add a custom thumbnail\n**/delthumb** : Delete your thumbnail\n**/report** : Report an issue (reply to a message)\n**/commands** : This list\n    "
    ADMINCMD = "\n**👑 Admin Commands**\n\n**/gitpull** : Update from GitHub\n**/broadcast** : Message all users\n**/sendto** : Message a specific user\n**/ban** : Ban user\n**/unban** : Unban user\n**/user** : View user stats\n**/user2** : Get Telegram User info\n**/self** : Get bot info\n**/getthumbs** : View all custom thumbnails\n**/maintenance** : Toggle maintenance mode\n**/cleanall** : Wipe all files\n**/cleantasks** : Wipe files & tasks\n**/logs** : Get bot logs\n**/restart** : Restart the bot\n**/eval** : Run Python code\n**/exec** : Run Shell code\n    "

    # custom_thumbnail.py
    ALBUM = "⚠️ User {} tried to set an album as thumbnail."
    ALBUM_NOPE = "⚠️ Please reply to a single photo, not an album or document."
    DL_THUMB = "📥 Downloading thumbnail..."
    THUMB_SAVED = "✅ Thumbnail saved."
    THUMB_CAPTION = "\n🖼️ **Thumbnail**\n\nSaved for [User](tg://user?id={})\n    "
    THUMB_FAILED = "❌ Failed to generate thumbnail."
    THUMB_ERROR = "❌ Error processing thumbnail. Try again."
    NO_THUMB = "⚠️ You don't have a custom thumbnail set."

    # ext_helper.py
    UP_ALL = "📤 Upload All"
    CANCEL_IT = "❌ Cancel"

    # up_helper.py
    TRY_UP = "\n📤 **Uploading `{}`...**\n\n    "
    CANT_FIND = "❌ File not found: `{}`"
    TOO_LARGE = "❌ URL file exceeds Telegram limits."
    ARCHIVE_GONE = "❌ Archive deleted before upload."
    EMPTY_FILE = "❌ File `{}` is empty."
    CHECK_MSG = "\n🔍 **Verifying file...**\n\n    "


# List of error messages from p7zip
ERROR_MSGS = ["Error", "Can't open as archive"]


# Inline buttons
class Buttons:
    START_BUTTON = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(Messages.HELP, callback_data="helpcallback"),
                InlineKeyboardButton(Messages.ABOUT, callback_data="aboutcallback"),
            ],
            [
                InlineKeyboardButton(Messages.STATS_BTN, callback_data="statscallback"),
                InlineKeyboardButton(Messages.DONATE, callback_data="donatecallback"),
            ],
        ]
    )

    REFRESH_BUTTON = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    Messages.REFRESH, callback_data="statscallback|refresh"
                ),
                InlineKeyboardButton(Messages.BACK, callback_data="megoinhome"),
            ]
        ]
    )

    CHOOSE_E_F__BTNS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🗂️", callback_data="extract_file|tg_file|no_pass"),
                InlineKeyboardButton(
                    "🔐", callback_data="extract_file|tg_file|with_pass"
                ),
            ],
            [
                InlineKeyboardButton("🖼️", callback_data="extract_file|tg_file|thumb"),
                InlineKeyboardButton(
                    "✏", callback_data="extract_file|tg_file|thumbrename"
                ),
            ],
            [InlineKeyboardButton("❌", callback_data="cancel_dis")],
        ]
    )

    CHOOSE_E_F_M__BTNS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🗂️", callback_data="merged|no_pass"),
                InlineKeyboardButton("🔐", callback_data="merged|with_pass"),
            ],
            [InlineKeyboardButton("❌", callback_data="cancel_dis")],
        ]
    )

    CHOOSE_E_U__BTNS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("🔗", callback_data="extract_file|url|no_pass"),
                InlineKeyboardButton("🔐", callback_data="extract_file|url|with_pass"),
            ],
            [
                InlineKeyboardButton("🖼️", callback_data="extract_file|url|thumb"),
                InlineKeyboardButton("✏", callback_data="extract_file|url|thumbrename"),
            ],
            [InlineKeyboardButton("❌", callback_data="cancel_dis")],
        ]
    )

    RENAME = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("✏", callback_data="renameit"),
                InlineKeyboardButton("🙅‍♂️", callback_data="norename"),
            ]
        ]
    )

    CLN_BTNS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(Messages.CLEAN, callback_data="cancel_dis"),
                InlineKeyboardButton(Messages.CANCEL_IT, callback_data="nobully"),
            ]
        ]
    )

    ME_GOIN_HOME = InlineKeyboardMarkup(
        [[InlineKeyboardButton(Messages.BACK, callback_data="megoinhome")]]
    )

    SET_UPLOAD_MODE_BUTTONS = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(Messages.AS_DOC, callback_data="set_mode|doc"),
                InlineKeyboardButton(Messages.AS_MEDIA, callback_data="set_mode|media"),
            ],
        ]
    )

    I_PREFER_STOP = InlineKeyboardMarkup(
        [[InlineKeyboardButton(Messages.CANCEL_IT, callback_data="canceldownload")]]
    )

    MERGE_THEM_ALL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(Messages.MERGE_BTN, callback_data="merge_this"),
                InlineKeyboardButton(Messages.CANCEL_IT, callback_data="cancel_dis"),
            ]
        ]
    )

    THUMB_REPLACEMENT = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(Messages.CHECK, callback_data="check_thumb"),
                InlineKeyboardButton(
                    Messages.REPLACE, callback_data="save_thumb|replace"
                ),
            ],
            [InlineKeyboardButton(Messages.CANCEL_IT, callback_data="nope_thumb")],
        ]
    )

    THUMB_FINAL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    Messages.REPLACE, callback_data="save_thumb|replace"
                ),
                InlineKeyboardButton(Messages.CANCEL_IT, callback_data="nope_thumb"),
            ]
        ]
    )

    THUMB_SAVE = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(Messages.SAVE, callback_data="save_thumb|save"),
                InlineKeyboardButton(Messages.CANCEL_IT, callback_data="nope_thumb"),
            ]
        ]
    )

    THUMB_DEL = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(Messages.CHECK, callback_data="check_before_del"),
                InlineKeyboardButton(Messages.DELETE, callback_data="del_thumb"),
            ],
            [InlineKeyboardButton(Messages.CANCEL_IT, callback_data="nope_thumb")],
        ]
    )

    THUMB_DEL_2 = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(Messages.DELETE, callback_data="del_thumb"),
                InlineKeyboardButton(Messages.CANCEL_IT, callback_data="nope_thumb"),
            ],
        ]
    )

    RATE_ME = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    Messages.RATE, url="https://t.me/BotsArchive/2705"
                ),
                InlineKeyboardButton(Messages.DONATE, callback_data="donatecallback"),
            ],
        ]
    )
