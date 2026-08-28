import telebot
from telebot import types

# 🔑 የቦትህ Token
TOKEN = "8696066666:AAEOXsx_Gr4nU_vvVfTZmcc-un6Q-EZSEVA"
bot = telebot.TeleBot(TOKEN)

# 👤 የ Admin Telegram User ID
ADMIN_ID = 8876708584

# 🔒 ትክክለኛው የ VIP Private ቻናልህ ID
CHANNEL_ID = -1004465601435

# 🚀 1. ተጠቃሚው /start ሲል የሚሰራ ኮድ
@bot.message_handler(commands=['start'])
def send_welcome(message):
    welcome_text = (
        "👋 እንኳን ወደ VIP ቻናል አባልነት ቦት በደህና መጡ!\n\n"
        "💳 **የአባልነት ክፍያ:** 200 ብር\n\n"
        "🏦 **የክፍያ አማራጮች:**\n"
        "• **CBE:** 1000722602017\n"
        "• **Telebirr:** 0971904060\n\n"
        "ወደ VIP ቻናል ለመቀላቀል፣ የከፈሉበትን ደረሰኝ (የክፍያ ፎቶ ወይም SMS) እዚህ ይላኩ!"
    )
    bot.reply_to(message, welcome_text)

# 📸 2. ተጠቃሚው ደረሰኝ (ፎቶ) ሲልክ ወደ Admin የሚያስተላልፍ ኮድ
@bot.message_handler(content_types=['photo'])
def handle_photo(message):
    user_id = message.from_user.id
    username = message.from_user.username or "የሌለው"
    
    # ለተጠቃሚው ማረጋገጫ መላክ
    bot.reply_to(
        message, 
        "✅ ደረሰኝዎ ደርሶናል! መረጃውን አረጋግጠን የ VIP ቻናሉን የመግቢያ ሊንክ በአጭር ጊዜ ውስጥ እንልካለን።"
    )
    
    # የማረጋገጫ ቁልፎች (Inline Buttons) መፍጠር
    markup = types.InlineKeyboardMarkup()
    approve_btn = types.InlineKeyboardButton("✅ አጽድቅ", callback_data=f"approve_{user_id}")
    reject_btn = types.InlineKeyboardButton("❌ ውድቅ አድርግ", callback_data=f"reject_{user_id}")
    markup.add(approve_btn, reject_btn)
    
    user_info = f"📩 **አዲስ ደረሰኝ ደርሷል!**\n\n👤 **ተጠቃሚ:** @{username}\n🆔 **ID:** `{user_id}`"
    bot.send_photo(ADMIN_ID, message.photo[-1].file_id, caption=user_info, reply_markup=markup, parse_mode="Markdown")

# 🔘 3. Admin ቁልፎቹን ሲነካ የሚሰራ ኮድ (Callback Handler)
@bot.callback_query_handler(func=lambda call: True)
def handle_buttons(call):
    data = call.data.split("_")
    action = data[0]
    target_user_id = int(data[1])
    
    if action == "approve":
        try:
            # 🔗 ለአንድ ሰው ብቻ የሚሰራ የቻናል መግቢያ ሊንክ በራሱ ጊዜ መፍጠር (member_limit=1)
            invite_link = bot.create_chat_invite_link(
                chat_id=CHANNEL_ID,
                member_limit=1
            )
            
            # ለተጠቃሚው ሊንኩን መላክ
            success_text = (
                "🎉 **ክፍያዎ ተረጋግጧል!**\n\n"
                f"ወደ VIP ቻናላችን ለመቀላቀል ይህንን የ1 ጊዜ መግቢያ ሊንክ ይጠቀሙ፦\n{invite_link.invite_link}"
            )
            bot.send_message(target_user_id, success_text)
            bot.answer_callback_query(call.id, "✅ ጸድቋል! የቻናሉ ሊንክ ለተጠቃሚው ተልኳል።")
            bot.edit_message_caption("✅ **ይህ ደረሰኝ ጸድቋል!**", chat_id=call.message.chat.id, message_id=call.message.message_id)
            
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ ስህተት ተከሰተ፡ ቦቱ የቻናሉ አድሚን መሆኑን ያረጋግጡ!", show_alert=True)
        
    elif action == "reject":
        # ለተጠቃሚው የማሳወቂያ መልእክት መላክ
        reject_text = "❌ **ይቅርታ!** የላኩት ደረሰኝ አልተረጋገጠም። እባክዎን ትክክለኛውን የክፍያ ደረሰኝ እንደገና ይላኩ።"
        bot.send_message(target_user_id, reject_text)
        bot.answer_callback_query(call.id, "❌ ውድቅ አድርገሃል።")
        bot.edit_message_caption("❌ **ይህ ደረሰኝ ውድቅ ተደርጓል!**", chat_id=call.message.chat.id, message_id=call.message.message_id)

# 🔄 ቦቱ ሁልጊዜ ክፍት ሆኖ እንዲሰራ
bot.polling()

