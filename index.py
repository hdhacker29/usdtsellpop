from dotenv import load_dotenv
load_dotenv()
import os
import asyncio, re, random, string
from aiogram import Bot, Dispatcher, types
from aiogram.filters import Command
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from key import main_menu
from database import admin_update_order


from database import (
    save_user, update_upi,
    create_order, update_order_amount,
    get_orders, get_user_by_uid
)

BOT_TOKEN = os.environ.get("BOT_TOKENs")
if not BOT_TOKEN:
    print("Error: BOT_TOKEN environment variable nahi mila.")
    exit()
USDT_ADDRESS = os.environ.get("USDT_ADDRESS")
if not USDT_ADDRESS:
    print("Error: USDT_ADDRESS environment variable nahi mila.")
    exit()

ADMIN_CHAT_ID = os.environ.get("ADMIN_CHAT_ID")
if not ADMIN_CHAT_ID:
    print("Error: ADMIN_CHAT_ID environment variable nahi mila.")
    exit()

RUNNING_PRICE = 106.13
TIME_LIMIT_MIN = 30

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher()
#ADMIN_CHAT_ID = 7464018948  # 👈 apna chat id


UPI_REGEX = r"^[a-zA-Z0-9.\-_]{2,256}@[a-zA-Z]{2,64}$"



session_uid = {}        # chat_id -> uid
user_step = {}          # chat_id -> UPI / AMOUNT
pending_amount = {}     # chat_id -> order_id


# ------------------------
# HELPERS
# ------------------------
def generate_uid():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=7))


async def send_usdt_ranges(chat_id):
    await bot.send_message(
        chat_id,
        "💱 *USDT Deposit Information*\n\n"
        "USDT (Tether) is a stable digital currency pegged to the US Dollar and widely used for secure and fast transactions.\n\n"
        "By depositing USDT, you can easily buy or sell digital assets at the current market rate with full transparency.\n\n"
        f"📈 *Running Price:* ₹{RUNNING_PRICE}\n"
        "⏱ *Processing Time:* Usually completed shortly after confirmation\n"
        "🔒 *Security:* Your transaction is manually verified for safety\n\n"
        "--- WELL CYPTO USDT --- ",
        
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="800 – 2999 USDT", callback_data="usdt_1")],
            [InlineKeyboardButton(text="3000 – 9999 USDT", callback_data="usdt_2")],
            [InlineKeyboardButton(text="10000 – 14999 USDT", callback_data="usdt_3")],
            [InlineKeyboardButton(text="15000 – 49999 USDT", callback_data="usdt_4")]
        ])
    )


# ------------------------
# START
# ------------------------
@dp.message(Command("start"))
async def start(msg: types.Message):
    chat_id = msg.chat.id

    if chat_id not in session_uid:
        uid = generate_uid()
        session_uid[chat_id] = uid
        save_user(uid, chat_id)
    else:
        uid = session_uid[chat_id]

    user_step[chat_id] = "UPI"

    await msg.answer(
        f"Congratulations 🎉 Uking \n"
        f" Welcome......\n"
        f"🆔 Your UID: `{uid}`\n\n"
        f"Please Enter Your POP-ID(UPI) IN:",
        reply_markup=main_menu,
        parse_mode="Markdown"
    )


# ------------------------
# ORDERS BUTTON
# ------------------------
@dp.message(lambda m: m.text == "📦 Orders")
async def orders_btn(msg: types.Message):
    chat_id = msg.chat.id

    if chat_id not in session_uid:
        await msg.answer("⚠ Please /start first")
        return

    uid = session_uid[chat_id]
    orders = get_orders(uid)

    if not orders:
        await msg.answer("❌ No orders found")
        return

    text = "📦 *Your Orders*\n\n"
    for o in orders:
        text += (
            f"🆔 Order ID: {o[0]}\n"
            f"💰 USDT Amount: {o[1]}\n"
            f"📌 Status: {o[2]}\n"
            f"🕒 Time: {o[3]}\n"
            f"──────────────\n"
        )

    await msg.answer(text, parse_mode="Markdown")


# ------------------------
# YOUR UPI ACCOUNT BUTTON
# ------------------------
@dp.message(lambda m: m.text == "💳 Your UPI Account")
async def upi_account_btn(msg: types.Message):
    chat_id = msg.chat.id

    if chat_id not in session_uid:
        await msg.answer("⚠ Please /start first")
        return

    uid = session_uid[chat_id]
    user = get_user_by_uid(uid)

    upi = user[2] if user and user[2] else "Not set"

    user_step[chat_id] = "UPI"

    await msg.answer(
        f"🧾 *Your Account*\n\n"
        f"🆔 UID: `{uid}`\n"
        f"💳 UPI: `{upi}`\n\n"

        f"🌐PAYMENT WILL BE CREDITED YOUR UPI WALLET",
        parse_mode="Markdown"
    )


# ------------------------
# TEXT HANDLER (ONLY UPI / AMOUNT)
# ------------------------
@dp.message(lambda m: user_step.get(m.chat.id) in ["UPI", "AMOUNT"])
async def text_handler(msg: types.Message):
    chat_id = msg.chat.id
    text = msg.text.strip()

    # block buttons
    if text in ["📦 Orders", "💳 Your UPI Account"]:
        return

    if chat_id not in session_uid:
        return

    step = user_step.get(chat_id)

    # UPI STEP
    if step == "UPI":
        if not re.match(UPI_REGEX, text):
            await msg.answer("❌ Invalid POP ID\nEnter correct POP:")
            return

        uid = session_uid[chat_id]
        update_upi(uid, text)
        user_step[chat_id] = None

        await msg.answer("✅ UPI saved successfully\n\n--- POP-IN CREATED --- \n\n||ᵎᵎ WELL EARNING ᵎᵎ||", reply_markup=main_menu)
        await send_usdt_ranges(chat_id)
        return

    # AMOUNT STEP
    if step == "AMOUNT":
        try:
            amount = float(text)
        except:
            await msg.answer("❌ Enter numeric amount (example: 900)")
            return

        if not (800 <= amount <= 49999):
            await msg.answer("❌ Amount out of range")
            return

        order_id = pending_amount.pop(chat_id)
        update_order_amount(order_id, amount)
        user_step[chat_id] = None

        await msg.answer(
            f"📥 *SEND USDT AMOUNT IN ADDRESS ₮💵*\n\n"
            f"`{USDT_ADDRESS}`\n\n"
            f"🆔 Order ID: {order_id}\n"
            f"💰 Amount: {amount} USDT\n"
            f"📌 Status: PENDING\n"
            f"⏱ Time limit: {TIME_LIMIT_MIN} minutes",
            parse_mode="Markdown",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(
                    text="✅ BUY CONFIRM(ORDER)",
                    callback_data=f"sell_{order_id}"
                )]
            ])
        )


# ------------------------
# RANGE SELECT
# ------------------------
@dp.callback_query(lambda c: c.data.startswith("usdt_"))
async def usdt_selected(cb: types.CallbackQuery):
    uid = session_uid[cb.message.chat.id]
    order_id = create_order(uid)

    pending_amount[cb.message.chat.id] = order_id
    user_step[cb.message.chat.id] = "AMOUNT"

    await cb.message.answer(
        "PLEASE IMPORT HOW MANY BUY USDT 💵₮ (AMOUNT)",
        parse_mode="Markdown"
    )


# ------------------------
# SELL CONFIRM
# ------------------------
@dp.callback_query(lambda c: c.data.startswith("sell_"))
async def sell_confirm(cb: types.CallbackQuery):
    await cb.answer()
    await cb.message.answer(
        "OVER TEAM SHARED YOU WILL GET RESPONSE SOMETIME ⋆˚꩜｡ \n\n PLEASE SURE YOU SEND USDT RIGHT NOW ◝(ᵔᵕᵔ)◜",
        parse_mode="Markdown"
    )


# ------------------------
# MAIN
# ------------------------
async def main():
    print("🤖 Bot running (FINAL CLEAN)")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
