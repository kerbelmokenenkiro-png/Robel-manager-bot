import os
import random
from threading import Thread
from flask import Flask
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters

# 1. Flask Web Server (ለ UptimeRobot/Render)
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Robel Manager Bot is Active!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    web_app.run(host='0.0.0.0', port=port)

# 2. የውሂብ መዝገብ (In-Memory Database for Scores)
user_scores = {}

# 3. የጥያቄዎች ስብስብ (Quiz Database)
QUIZ_DATA = [
    {
        "question": "የኮምፒውተር አእምሮ (Brain) በመባል የሚታወቀው የትኛው ክፍል ነው? 🧠",
        "options": [
            InlineKeyboardButton("A) RAM", callback_data='quiz_wrong'),
            InlineKeyboardButton("B) CPU", callback_data='quiz_correct'),
            InlineKeyboardButton("C) Hard Drive", callback_data='quiz_wrong')
        ]
    },
    {
        "question": "በአለም ላይ የመጀመሪያው የኮምፒውተር ፕሮግራመር ማን ናት/ነው? 💻",
        "options": [
            InlineKeyboardButton("A) Alan Turing", callback_data='quiz_wrong'),
            InlineKeyboardButton("B) Ada Lovelace", callback_data='quiz_correct'),
            InlineKeyboardButton("C) Bill Gates", callback_data='quiz_wrong')
        ]
    },
    {
        "question": "የቴሌግራም መተግበሪያ የተመሰረተው በየትኛው ዓመተ ምህረት ነው? 📱",
        "options": [
            InlineKeyboardButton("A) 2013", callback_data='quiz_correct'),
            InlineKeyboardButton("B) 2010", callback_data='quiz_wrong'),
            InlineKeyboardButton("C) 2015", callback_data='quiz_wrong')
        ]
    },
    {
        "question": "Python የፕሮግራሚንግ ቋንቋ የተሰራው በምንድነው? 🐍",
        "options": [
            InlineKeyboardButton("A) C Language", callback_data='quiz_correct'),
            InlineKeyboardButton("B) Java", callback_data='quiz_wrong'),
            InlineKeyboardButton("C) C++", callback_data='quiz_wrong')
        ]
    },
    {
        "question": "በበይነመረብ (Internet) ላይ መረጃዎችን በደህና ለመላክ የሚያገለግለው ፕሮቶኮል የትኛው ነው? 🔐",
        "options": [
            InlineKeyboardButton("A) HTTP", callback_data='quiz_wrong'),
            InlineKeyboardButton("B) HTTPS", callback_data='quiz_correct'),
            InlineKeyboardButton("C) FTP", callback_data='quiz_wrong')
        ]
    }
]

# 4. የቴክኖሎጂ እውነታዎች (Tech Facts)
TECH_FACTS = [
    "💡 የመጀመሪያው 1GB Hard Drive በ 1980 የወጣ ሲሆን ሚዛኑ ከ 250 ኪሎግራም በላይ ነበር!",
    "💡 በየቀኑ ከ 500 ሚሊዮን በላይ ቴ tweet በ Twitter (X) ላይ ይላካሉ።",
    "💡 የመጀመሪያው የኮምፒውተር ማውስ (Mouse) የተሰራው ከእንጨት ነበር።",
    "💡 በዓለም ላይ ካለው ገንዘብ 92% የሚሆነው በዲጂታል መልክ ብቻ ነው ያለው፤ የካሽ ኖት አይደለም።",
    "💡 ሮቦት (Robot) የሚለው ቃል የመጣው 'Robota' ከሚለው የቼክ ቃል ሲሆን ትርጉሙም 'የግዳጅ ስራ' ማለት ነው።"
]

# 5. ዋና ዋና ተግባራት (Bot Handlers)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_name = update.effective_user.first_name
    keyboard = [
        [
            InlineKeyboardButton("🎮 የጥያቄ ጨዋታ", callback_data='btn_quiz'),
            InlineKeyboardButton("📊 የእኔ ነጥብ", callback_data='btn_score')
        ],
        [
            InlineKeyboardButton("💡 የቴክ እውነታዎች", callback_data='btn_fact'),
            InlineKeyboardButton("🧮 ካልኩሌተር", callback_data='btn_calc_help')
        ],
        [
            InlineKeyboardButton("ℹ️ ስለ ቦቱ", callback_data='btn_about')
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    welcome_text = (
        f"ሰላም {user_name}! 👋\n"
        f"እንኳን ወደ **Robel Manager Bot** በደህና መጡ! 🤖\n\n"
        f"ከታች ያሉትን ቁልፎች በመጫን የሚፈልጉትን አገልግሎት መምረጥ ይችላሉ፦"
    )
    if update.message:
        await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')
    elif update.callback_query:
        await update.callback_query.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode='Markdown')

async def send_quiz(query_or_message):
    q_data = random.choice(QUIZ_DATA)
    keyboard = [[opt] for opt in q_data["options"]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    if hasattr(query_or_message, 'edit_message_text'):
        await query_or_message.edit_message_text(q_data["question"], reply_markup=reply_markup)
    else:
        await query_or_message.reply_text(q_data["question"], reply_markup=reply_markup)

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    user_id = query.from_user.id
    user_name = query.from_user.first_name

    # የጥያቄዎች ምላሽ
    if query.data == 'quiz_correct':
        user_scores[user_id] = user_scores.get(user_id, 0) + 10
        keyboard = [
            [InlineKeyboardButton("🔄 ሌላ ጥያቄ", callback_data='btn_quiz')],
            [InlineKeyboardButton("🏠 ወደ ዋናው ገጽ", callback_data='btn_main_menu')]
        ]
        await query.edit_message_text(
            f"ትክክል ነህ! 🎉 +10 ነጥብ አግኝተሃል።\nአጠቃላይ ነጥብህ፦ {user_scores[user_id]}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    elif query.data == 'quiz_wrong':
        keyboard = [
            [InlineKeyboardButton("🔄 ሌላ ጥያቄ ለመሞከር", callback_data='btn_quiz')],
            [InlineKeyboardButton("🏠 ወደ ዋናው ገጽ", callback_data='btn_main_menu')]
        ]
        await query.edit_message_text(
            f"ተሳስተሃል! ❌ እንደገና ሞክር።\nአሁናዊ ነጥብህ፦ {user_scores.get(user_id, 0)}",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    
    # የቁልፎች ምላሽ (Menu Buttons)
    elif query.data == 'btn_quiz':
        await send_quiz(query)
        
    elif query.data == 'btn_score':
        score = user_scores.get(user_id, 0)
        keyboard = [[InlineKeyboardButton("🏠 ወደ ዋናው ገጽ", callback_data='btn_main_menu')]]
        await query.edit_message_text(
            f"🏆 **የነጥብ መዝገብ**\n\nተጠቃሚ፦ {user_name}\nያለህ አጠቃላይ ነጥብ፦ {score} ነጥብ",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
        
    elif query.data == 'btn_fact':
        fact = random.choice(TECH_FACTS)
        keyboard = [
            [InlineKeyboardButton("💡 ሌላ እውነታ", callback_data='btn_fact')],
            [InlineKeyboardButton("🏠 ወደ ዋናው ገጽ", callback_data='btn_main_menu')]
        ]
        await query.edit_message_text(f"**የዕለቱ የቴክ እውነታ፦**\n\n{fact}", reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif query.data == 'btn_calc_help':
        keyboard = [[InlineKeyboardButton("🏠 ወደ ዋናው ገጽ", callback_data='btn_main_menu')]]
        calc_text = (
            "🧮 **የካልኩሌተር አጠቃቀም**\n\n"
            "ሂሳብ ለማስላት የመደመር፣ የመቀነስ፣ የማባዛትና የማካፈል ምልክቶችን በመጠቀም ይጻፉ።\n\n"
            "ምሳሌ፦ `/calc 25 * 4` ወይም `/calc 100 / 5`"
        )
        await query.edit_message_text(calc_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif query.data == 'btn_about':
        keyboard = [[InlineKeyboardButton("🏠 ወደ ዋናው ገጽ", callback_data='btn_main_menu')]]
        about_text = (
            "🤖 **ስለ Robel Manager Bot**\n\n"
            "ይህ ቦት በ Python የተሰራ ሲሆን ለጨዋታዎች፣ ለሂሳብ ስሌቶች እና ለተለያዩ መረጃዎች አገልግሎት ይሰጣል።\n\n"
            "👨‍💻 አዘጋጅ፦ ሮቤል"
        )
        await query.edit_message_text(about_text, reply_markup=InlineKeyboardMarkup(keyboard), parse_mode='Markdown')

    elif query.data == 'btn_main_menu':
        keyboard = [
            [
                InlineKeyboardButton("🎮 የጥያቄ ጨዋታ", callback_data='btn_quiz'),
                InlineKeyboardButton("📊 የእኔ ነጥብ", callback_data='btn_score')
            ],
            [
                InlineKeyboardButton("💡 የቴክ እውነታዎች", callback_data='btn_fact'),
                InlineKeyboardButton("🧮 ካልኩሌተር", callback_data='btn_calc_help')
            ],
            [
                InlineKeyboardButton("ℹ️ ስለ ቦቱ", callback_data='btn_about')
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await query.edit_message_text(
            f"ሰላም {user_name}! 👋\nወደ ዋናው ማውጫ ተመልሰዋል። የሚፈልጉትን ይምረጡ፦",
            reply_markup=reply_markup
        )

# 6. የካልኩሌተር Command (Command Handler)
async def calculate(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("እባክዎን ከትእዛዙ በኋላ ስሌቱን ይጻፉ! ምሳሌ፦ `/calc 12 + 5`", parse_mode='Markdown')
        return
    
    expression = "".join(context.args)
    try:
        # ለደህንነት ሲባል የተወሰኑ ምልክቶችን ብቻ መፍቀድ
        allowed_chars = "0123456789+-*/.()"
        if any(char not in allowed_chars for char in expression):
            await update.message.reply_text("❌ እባክዎን ትክክለኛ የሂሳብ ምልክቶችን ብቻ ይጠቀሙ (+, -, *, /)")
            return
            
        result = eval(expression)
        await update.message.reply_text(f"🧮 **ውጤት፦** `{expression} = {result}`", parse_mode='Markdown')
    except Exception:
        await update.message.reply_text("❌ የጻፉት ስሌት ስህተት አለበት። እባክዎን አስተካክለው ይሞክሩ።")

# 7. ዋናው ማስነሻ አፕሊኬሽን (Main Application)
def main():
    # Flask ሰርቨርን በጀርባ ማስነሳት
    server_thread = Thread(target=run_flask)
    server_thread.daemon = True
    server_thread.start()

    # Telegram Bot Token setup
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "8693907353:AAFSnUHjcZtNXKiR6FBOWwg1oc41LildIdI")
    app = ApplicationBuilder().token(BOT_TOKEN).build()

    # Handlers ማገናኘት
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("quiz", lambda u, c: send_quiz(u.message)))
    app.add_handler(CommandHandler("calc", calculate))
    app.add_handler(CallbackQueryHandler(handle_callback))

    print("Robel Manager Bot Version 2.0 is running...")
    app.run_polling()

if __name__ == '__main__':
    main()

