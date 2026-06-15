import os
import re
import requests
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

# --- 1. WEB SERVER FOR RENDER ---
# Render (Free Plan) မှာ Bot ကို ၂၄ နာရီလုံး အသက်ရှင်နေစေဖို့ Web Port တစ်ခု ဖွင့်ပေးထားခြင်း ဖြစ်ပါတယ်
app = Flask('')

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_web_server():
    # Render က ပေးမယ့် PORT ကို ယူသုံးပါမယ်၊ မရှိရင် 8080 ကို သုံးပါမယ်
    port = int(os.environ.get("PORT", 8080))
    app.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_web_server)
    t.start()


# --- 2. TELEGRAM BOT LOGIC ---
# /start command အတွက် တုံ့ပြန်ချက်
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    welcome_text = (
        "👋 မင်္ဂလာပါဗျာ။ Mobile Legends Username & Region Checker Bot မှ ကြိုဆိုပါတယ်။\n\n"
        "🔎 *စစ်ဆေးရန်အတွက် အောက်ပါအတိုင်း ပေးပို့ပါ -*\n"
        "`/check [ID] [Server]`\n\n"
        "💡 _ဥပမာ -_ `/check 12345678 1234`"
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

# /check command အတွက် တုံ့ပြန်ချက်
async def check_mlbb(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # User ပေးလိုက်တဲ့ Args (ID နဲ့ Server) ကို ယူခြင်း
    if not context.args or len(context.args) < 2:
        await update.message.reply_text(
            "❌ *အသုံးပြုပုံ မှားယွင်းနေပါသည်။*\n"
            "မှန်ကန်သော ပုံစံ - `/check 12345678 1234`", 
            parse_mode="Markdown"
        )
        return

    ml_id = context.args[0]
    ml_server = context.args[1]

    await update.message.reply_text("⏳ *ခဏစောင့်ပေးပါ... စစ်ဆေးနေပါတယ်...*", parse_mode="Markdown")

    try:
        # API URL ဆောက်ခြင်း
        api_url = f"https://yanjiestore.com/submitt.php?ID={ml_id}&server={ml_server}"
        
        # API ထံ Request ပို့ခြင်း
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(api_url, headers=headers, timeout=10)
        raw_html = response.text

        # Regex အသုံးပြုပြီး Nickname နှင့် Country ကို ဖြတ်ထုတ်ခြင်း
        nickname_match = re.search(r'Nickname:\s*([^<\n\r]+)', raw_html)
        country_match = re.search(r'Akun Dibuat Negara:\s*([^<\n\r]+)', raw_html)

        nickname = nickname_match.group(1).strip() if nickname_match else "Unknown"
        country = country_match.group(1).strip() if country_match else "Unknown"

        # ရလဒ် ထုတ်ပေးခြင်း
        if nickname != "Unknown":
            result_text = (
                "🎮 *Mobile Legends Account Details*\n\n"
                "📝 *Nickname:* `{}`\n"
                "🆔 *ID:* `{}` ({})\n"
                "🌍 *Region:* `{}`"
            ).format(nickname, ml_id, ml_server, country)
            
            await update.message.reply_text(result_text, parse_mode="Markdown")
        else:
            await update.message.reply_text("❌ *Account ရှာမတွေ့ပါ။* ID နှင့် Server ပြန်စစ်ပေးပါ။", parse_mode="Markdown")

    except Exception as e:
        print(f"Error: {e}")
        await update.message.reply_text("❌ *စစ်ဆေးရတာ မအောင်မြင်ပါ။* API Server မှာ Error တက်နေပါသည်။")


# --- 3. MAIN RUNNER ---
def main():
    # သင့်ရဲ့ Telegram Bot Token ကို ဤနေရာတွင် တိုက်ရိုက်ထည့်သွင်းပေးထားပါတယ်
    BOT_TOKEN = "8602797884:AAG5IWbaUExoFs1GwWVsDsl8qUvwobMShzs"

    # Web Server ကို နောက်ကွယ်ကနေ အလုပ်လုပ်ခိုင်းခြင်း
    keep_alive()

    # Telegram Bot ကို စတင်ခြင်း
    application = Application.builder().token(BOT_TOKEN).build()

    # Command Handler များ ထည့်သွင်းခြင်း
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("check", check_mlbb))

    # Bot ကို Polling စနစ်ဖြင့် ပတ်ခြင်း
    print("🚀 Bot is starting with your token...")
    application.run_polling()

if __name__ == '__main__':
    main()
