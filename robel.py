import os
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# Flask Web Server
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# Telegram Bot Functions
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("ሰላም! እንኳን ወደ Robel Manager Bot በደህና መጡ! 🤖\nየጥያቄና መልስ ጨዋታ ለመጫወት /quiz ብለው ይጻፉ።")

async def quiz(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("A) RAM", callback_data='wrong')],
        [InlineKeyboardButton("B) CPU", callback_data='correct')],
        [InlineKeyboardButton("C) Hard Drive", callback_data='wrong')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("ጥያቄ፦ የኮምፒውተር አእምሮ (Brain) በመባል የሚታወቀው የትኛው ክፍል ነው? 🧠", reply_markup=reply_markup)

async def button_click(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    if query.data == 'correct':
        await query.edit_message_text(text="ትክክል ነህ! 🎉 CPU የኮምፒውተር ዋና አእምሮ ነው።\nእንደገና ለመጫወት /quiz ብለህ ጻፍ።")
    else:
        await query.edit_message_text(text="ተሳስተሃል! ❌ እንደገና ለመሞከር /quiz ብለህ ጻፍ።")

def main():
    # Flask ሰርቨሩን በጀርባ ማስነሳት
    server_thread = Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()

    # Telegram Bot
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "YOUR_BOT_TOKEN_HERE")  # ወይም የራስህን ቶከን እዚህ ተጠቀም
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", quiz))
    app.add_handler(CallbackQueryHandler(button_click))

    print("Bot is running...")
    app.run_polling()

if __name__ == '__main__':
    main()
