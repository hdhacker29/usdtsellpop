import asyncio
import os
from aiogram import Bot
from dotenv import load_dotenv

from database import update_order_status, get_chat_id

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
bot = Bot(token=BOT_TOKEN)

async def send_status():
    uid = "SAJM36J"        # user UID
    order_id = 34         # order id
    status = "COMPLETED"  # PENDING / PROCESSING / COMPLETED / FAILED

    # 1️⃣ DB update
    update_order_status(order_id, status)

    # 2️⃣ user chat id
    chat_id = get_chat_id(uid)

    # 3️⃣ Telegram message
    if chat_id:
        await bot.send_message(
            chat_id,
            f"✅ Payment Verified\n\n"
            f"🆔 Order ID: {order_id}\n"
            f"📌 Status: {status}"
        )
        print("✅ Status sent to user")
    else:
        print("❌ Chat ID not found")

    await bot.session.close()

asyncio.run(send_status())
