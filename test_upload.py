import asyncio
from pyrogram import Client
from config import Config

async def main():
    app = Client("unzipperbot", api_id=Config.APP_ID, api_hash=Config.API_HASH, bot_token=Config.BOT_TOKEN)
    await app.start()
    with open("dummy.bin", "wb") as f:
        f.write(b"0" * 1024)
    try:
        await app.send_video(chat_id=Config.BOT_OWNER, video="dummy.bin")
        print("Video success")
    except Exception as e:
        print("Video failed:", e)
    await app.stop()

asyncio.run(main())
