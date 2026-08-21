import os
import requests
import telebot

# 1. Environment Variables የማንበቢያ ክፍል 🔑
BOT_TOKEN = "8693907353:AAFSnUHjcZtNXKiR6FBOWwg1oc41LildIdI"
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

bot = telebot.TeleBot(BOT_TOKEN)

# 2. የ Gemini API ጥሪ ማድረጊያ ተግባር 🧠
def get_gemini_response(user_text):
    if not GEMINI_API_KEY:
        return "ስህተት፡ የ Gemini API Key አልተገኘም። በ Render Environment Variables ውስጥ GEMINI_API_KEY መጨመሩን ያረጋግጡ።"

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    data = {
        "contents": [{
            "parts": [{"text": user_text}]
        }]
    }

    try:
        response = requests.post(url, headers=headers, json=data)
        if response.status_code == 200:
            result = response.json()
            return result['candidates'][0]['content']['parts'][0]['text']
        else:
            return f"ይቅርታ፣ ከ AI መልስ ሲቀበል ስህተት ተፈጥሯል። (Status Code: {response.status_code})"
    except Exception as e:
        return f"ስህተት፡ {e}"

# 3. የቴሌግራም መልእክቶችን መቀበያ 📥
@bot.message_handler(func=lambda message: True)
def handle_message(message):
    user_input = message.text
    ai_response = get_gemini_response(user_input)
    bot.reply_to(message, ai_response)

print("ቦቱ መስራት ጀምሯል... 🚀")
bot.polling()
