import os
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes

# --- 🌐 Dummy Web Server ለ Render (PORT ችግርን ለመፍታት) ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "Bot is alive!"

def run_flask():
    # Render የሚሰጠውን PORT ወይም በደፈናው 8080 እንጠቀማለን
    port = int(os.environ.get("PORT", 8080))
    app_web.run(host='0.0.0.0', port=port)

def keep_alive():
    t = Thread(target=run_flask)
    t.daemon = True
    t.start()
# --------------------------------------------------------

# የቦቱ መረጃዎችና አዝራሮች በስርዓት የተደራጁበት መዝገበ-ቃላት
DATA = {
    "menu_fun": {
        "title": "🎭 የደስታና መዝናኛ ምድብ",
        "items": {
            "joke1": ("😄 ቀልድ 1", "አንድ ተማሪ '2+2 ስንት ነው?' ሲባል 'እንደ ሁኔታው ይለያያል' አለ!"),
            "joke2": ("😄 ቀልድ 2", "መምህር፦ 'የዓለማችን ትልቁ ነገር ምንድነው?' ተማሪ፦ 'የአባቴ ሆድ!'"),
            "quote1": ("💡 አባባል 1", "'ትልቁ ስኬት ውድቀትን ሳይፈሩ መሞከር ነው!'"),
            "quote2": ("💡 አባባል 2", "'ዛሬ የምትዘራው ነገ የምታጭደው ነው!'")
        }
    },
    "menu_edu": {
        "title": "📚 የትምህርትና ጥበብ ምድብ",
        "items": {
            "fact1": ("💻 የቴክኖሎጂ እውነታ", "የመጀመሪያው የኮምፒውተር ማውስ የተሰራው ከእንጨት ነበር!"),
            "fact2": ("🌍 የተፈጥሮ እውነታ", "የዓለማችን ረጅሙ ወንዝ አባይ (Nile) ነው!")
        }
    }
}

# ዋና ማውጫ (Main Menu)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🎭 የደስታና መዝናኛ ምድብ", callback_data='menu_fun')],
        [InlineKeyboardButton("📚 የትምህርትና ጥበብ ምድብ", callback_data='menu_edu')],
        [InlineKeyboardButton("ℹ️ ስለ ቦቱ", callback_data='about')]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = "<b>🌟 እንኳን ወደ ፕሮፌሽናል አጋዥ ቦት በደህና መጡ!</b>\n\nእባክዎ መመልከት የሚፈልጉትን ምድብ ይምረጡ፦"
    
    if update.message:
        await update.message.reply_text(text, parse_mode='HTML', reply_markup=reply_markup)
    else:
        await update.callback_query.edit_message_text(text, parse_mode='HTML', reply_markup=reply_markup)

# የአዝራሮች ምላሽ አስተናጋጅ
async def handle_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data
    
    if data == 'menu_main':
        await start(update, context)
    elif data in DATA:
        category = DATA[data]
        keyboard = []
        for item_id, (label, _) in category["items"].items():
            keyboard.append([InlineKeyboardButton(label, callback_data=f"info_{data}_{item_id}")])
        keyboard.append([InlineKeyboardButton("⬅️ ወደ ዋና ማውጫ", callback_data='menu_main')])
        await query.edit_message_text(f"<b>{category['title']}</b>\n\nአንዱን ይምረጡ፦", parse_mode='HTML', reply_markup=InlineKeyboardMarkup(keyboard))
    elif data.startswith("info_"):
        _, cat_key, item_id = data.split("_", 2)
        _, response_text = DATA[cat_key]["items"][item_id]
        await query.message.reply_text(response_text)
    elif data == 'about':
        await query.message.reply_text("ℹ️ <b>ስለ ቦቱ:</b>\nይህ በልዩ ሁኔታ የተሰራ ፕሮፌሽናል አጋዥ ቦት ነው! 🌟", parse_mode='HTML')

if __name__ == '__main__':
    # 1. ዌብ ሰርቨሩን ከበስተጀርባ ማስነሳት
    keep_alive()
    
    # 2. የቴሌግራም ቦቱን ማስነሳት
    TOKEN = "8693907353:AAFSnUHjcZtNXKiR6FBOWwg1oc41LildIdI"
    app = ApplicationBuilder().token(TOKEN).build()
    
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(handle_buttons))
    
    print("ፕሮፌሽናል ቦቱ ስራ ጀምሯል...")
    app.run_polling()
