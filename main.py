import os
import sqlite3
from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

API_ID = 33075883
API_HASH = "3bdc4f9c21f32c342fd745244686d99f"
BOT_TOKEN = "8545821473:AAHtjC2lJjBNRB7KOD-aRh2UjCOjzsCPvRU"

UPI_ID = "A.rawat.53@superyes"
QR_IMAGE_PATH = "qr_code.jpg"

PLANS_TEXT = """✨ **WHAT YOU GET WITH PREMIUM:**

✅ **UNLIMITED DAILY LINKS**
NO DAILY QUOTA — ACCESS ANY LINK, ANYTIME

✅ **FREE-LINK LIMIT BYPASS**
SKIP THE DAILY FREE-LINK RESTRICTION COMPLETELY

✅ **PROTECT-CONTENT BYPASS**
SAVE AND FORWARD EVERY FILE YOU RECEIVE

✅ **INSTANT AUTO-ACTIVATION**
UPI PAYMENT IS VERIFIED AUTOMATICALLY — NO WAITING

✅ **PRIORITY SUPPORT**
PREMIUM USERS GET HELP FASTER

──────────────
📋 **PREMIUM PLAN CHART**

💰 **Credit Packs:**
• 🥇 **10 Credits** — 🪙 ₹10
• 🥇 **50 Credits** — 🪙 ₹40
• 🥇 **100 Credits** — 🪙 ₹80

🌟 **VIP Pack:**
• 🥈 **1 Month Access** — 🪙 ₹299
• 🥈 **3 Month Access** — 🪙 ₹499

🔥 **Ultra VIP Pack:**
• 👑 **Lifetime Access** — 🪙 ₹799
• 👑 **Lifetime + 1200 Leaked MMS** — 🪙 ₹899

📲 **Payment ke liye niche diye gaye QR code ko scan karein ya UPI ID par payment bhejein:**
🆔 **UPI ID:** `{UPI_ID}`
"""

conn = sqlite3.connect('hosting_bot.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        credits INTEGER,
        plan TEXT DEFAULT 'Free'
    )
''')
conn.commit()

app = Client("hosting_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client, message):
    user_id = message.from_user.id
    cursor.execute("SELECT credits FROM users WHERE user_id = ?", (user_id,))
    user = cursor.fetchone()
    
    if not user:
        cursor.execute("INSERT INTO users (user_id, credits) VALUES (?, ?)", (user_id, 1))
        conn.commit()
        credit_msg = "🎁 Swagat hai! Aapko 1 Free Credit mil gaya hai."
    else:
        credit_msg = f"💼 Aapke paas abhi {user[0]} credits bache hain."

    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("💳 VIEW PLANS · PAY VIA UPI", callback_data="view_plans")],
        [InlineKeyboardButton("🔒 CLOSE", callback_data="close_menu")]
    ])

    await message.reply_text(
        f"👋 **Insta Viral Bot mein aapka swagat hai!**\n\n{credit_msg}\n\nNeeche diye gaye button par click karke saare plans aur QR code dekhein:",
        reply_markup=keyboard
    )

@app.on_callback_query(filters.regex("view_plans"))
async def view_plans_callback(client, callback_query):
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton("🔒 CLOSE", callback_data="close_menu")]
    ])
    
    chat_id = callback_query.message.chat.id
    formatted_text = PLANS_TEXT.format(UPI_ID=UPI_ID)
    
    if os.path.exists(QR_IMAGE_PATH):
        await client.send_photo(
            chat_id=chat_id,
            photo=QR_IMAGE_PATH,
            caption=formatted_text,
            reply_markup=keyboard
        )
        await callback_query.message.delete()
    else:
        await callback_query.message.edit_text(
            formatted_text + "\n\n⚠️ *Note: QR image nahi mili.*",
            reply_markup=keyboard
        )

@app.on_callback_query(filters.regex("close_menu"))
async def close_callback(client, callback_query):
    await callback_query.message.delete()

print("🤖 Bot Successfully Run Ho Raha Hai...")
app.run()
