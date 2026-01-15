from telethon import TelegramClient, events
import asyncio

API_ID = 29111381
API_HASH = "c86ad2e2fadf7016897e792c8e5f2be9"
BOT_TOKEN = "8526591366:AAGmJEI6bedKUS0FJY0n_qvv0EkQ2hLmU1w"

bot = TelegramClient("dasdasd", API_ID, API_HASH)

@bot.on(events.NewMessage())
async def fuckre(event):
    await event.respond("fssdf")





async def main():
    await bot.start(bot_token=BOT_TOKEN)
    print("Bot is running")
    await bot.run_until_disconnected()

if __name__ == "__main__":
    asyncio.run(main())
