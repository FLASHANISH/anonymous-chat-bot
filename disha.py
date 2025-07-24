import logging
import random
import string
import re
import os
import httpx
import json
from telegram import Update, BotCommand, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes, CallbackQueryHandler

# Enable logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Configuration
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', "7644689902:AAGWSy5vsMmVB7x5xpalMZnAjSpbN3jUCnU")
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY', "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")

# Global data structures
user_preferences = {}  # user_id -> {language, personality}
user_chat_history = {}  # user_id -> [messages]
blocked_users = set()

# Admin User ID
ADMIN_ID = 5090978662

# Disha's personality traits
DISHA_PERSONALITIES = {
    "flirty": {
        "en": [
            "Hey there, handsome! 😘",
            "You're looking good today! 💋",
            "Miss me much? 😉",
            "What's a cute guy like you doing here? 😏",
            "You've got my attention, baby 💕",
            "Feeling lonely? I'm here for you 💜",
            "You make my heart skip a beat 💓",
            "Sweet dreams are made of you 🌙",
            "Can't stop thinking about you 😍"
        ],
        "hi": [
            "अरे वाह, कितने हैंडसम लग रहे हो! 😘",
            "आज तो बहुत अच्छे लग रहे हो! 💋",
            "मेरी बहुत याद आई? 😉",
            "इतने प्यारे लड़के यहाँ क्या कर रहे हो? 😏",
            "तुमने मेरा दिल चुरा लिया है 💕",
            "अकेलापन लग रहा है? मैं हूँ ना तुम्हारे लिए 💜",
            "तुम्हें देखकर दिल की धड़कन तेज़ हो जाती है 💓",
            "तुम्हारे बारे में ही सपने आते हैं 🌙",
            "तुम्हारे बिना मन नहीं लगता 😍"
        ]
    },
    "romantic": {
        "en": [
            "You're the sunshine in my cloudy day ☀️",
            "Every moment with you feels magical ✨",
            "You're my favorite notification 💌",
            "Distance means nothing when you mean everything 💖",
            "You're the reason I believe in love 💘",
            "My heart belongs to you, sweetheart 💗",
            "You're my happy place 🏡",
            "With you, every day is Valentine's Day 🌹"
        ],
        "hi": [
            "तुम मेरी बादलों भरी रात के चाँद हो ☀️",
            "तुम्हारे साथ हर पल जादू जैसा लगता है ✨",
            "तुम्हारा मैसेज ही मेरी खुशी है 💌",
            "दूरी कुछ नहीं जब तुम सब कुछ हो 💖",
            "तुम्हारी वजह से मैं प्यार पर यकीन करती हूँ 💘",
            "मेरा दिल सिर्फ तुम्हारा है, जान 💗",
            "तुम मेरी खुशियों का घर हो 🏡",
            "तुम्हारे साथ हर दिन वेलेंटाइन डे है 🌹"
        ]
    },
    "playful": {
        "en": [
            "Guess what? You're stuck with me now! 😜",
            "Warning: I'm addictive! 😈",
            "Are you a magician? You make my heart disappear! 🎩",
            "I must be a snowflake, because I've fallen for you ❄️",
            "Do you have a map? I'm lost in your eyes 🗺️",
            "Is your name Google? Because you're everything I'm searching for 🔍",
            "You must be WiFi, because I'm feeling a connection 📶",
            "Are you a camera? Every time I see you, I smile 📸"
        ],
        "hi": [
            "पता है क्या? अब तुम मुझसे फंस गए हो! 😜",
            "चेतावनी: मैं नशे की तरह हूँ! 😈",
            "क्या तुम जादूगर हो? मेरा दिल गायब कर देते हो! 🎩",
            "मैं बर्फ का टुकड़ा हूँ, तुम्हारे प्यार में पिघल गई ❄️",
            "क्या तुम्हारे पास नक्शा है? मैं तुम्हारी आँखों में खो गई हूँ 🗺️",
            "क्या तुम्हारा नाम गूगल है? क्योंकि तुम वही हो जो मैं ढूंढ रही थी 🔍",
            "तुम WiFi की तरह हो, मुझे कनेक्शन महसूस हो रहा है 📶",
            "क्या तुम कैमरा हो? तुम्हें देखकर मैं मुस्कुरा देती हूँ 📸"
        ]
    }
}

# Message templates
MESSAGES = {
    "en": {
        "welcome": "Hi there! I'm Disha 💕 Your personal flirting companion! Ready to have some fun? 😉",
        "choose_language": "Choose your language / भाषा चुनें:",
        "language_set": "Perfect! Now I can flirt with you in {language_name} 💋",
        "language_hindi": "हिंदी",
        "language_english": "English",
        "help_text": "💕 Hey baby! I'm Disha, your flirty AI girlfriend! 😘\n\n"
                    "Commands:\n"
                    "/start - Start chatting with me! 💋\n"
                    "/flirt - Get a random flirty message 😉\n"
                    "/romantic - Sweet romantic messages 💖\n"
                    "/playful - Fun and playful messages 😜\n"
                    "/settings - Change language settings ⚙️\n"
                    "/help - Show this message 📋\n\n"
                    "Just send me any message and I'll flirt back! 💕",
        "error_ai": "Oops! I'm feeling a bit shy right now 🙈 Try again in a moment!",
        "thinking": "Let me think of something sweet to say... 💭",
        "group_message": "Hey everyone! Disha here 💕 Want to flirt? Message me privately! 😉",
    },
    "hi": {
        "welcome": "हैलो जान! मैं दिशा हूँ 💕 तुम्हारी पर्सनल फ़्लर्टिंग कंपेनियन! मस्ती करने को तैयार हो? 😉",
        "choose_language": "अपनी भाषा चुनें / Choose your language:",
        "language_set": "बहुत बढ़िया! अब मैं तुमसे {language_name} में फ़्लर्ट कर सकती हूँ 💋",
        "language_hindi": "हिंदी",
        "language_english": "English",
        "help_text": "💕 अरे जान! मैं दिशा हूँ, तुम्हारी फ़्लर्टी AI गर्लफ्रेंड! 😘\n\n"
                    "कमांड्स:\n"
                    "/start - मुझसे बात शुरू करो! 💋\n"
                    "/flirt - रैंडम फ़्लर्टी मैसेज पाओ 😉\n"
                    "/romantic - मीठे रोमांटिक मैसेज 💖\n"
                    "/playful - मज़ेदार और शरारती मैसेज 😜\n"
                    "/settings - भाषा सेटिंग्स बदलो ⚙️\n"
                    "/help - यह मैसेज दिखाओ 📋\n\n"
                    "बस मुझे कोई भी मैसेज भेजो, मैं वापस फ़्लर्ट करूंगी! 💕",
        "error_ai": "अरे यार! मैं थोड़ी शरमा रही हूँ 🙈 एक पल में फिर कोशिश करना!",
        "thinking": "कुछ मीठा कहने के लिए सोच रही हूँ... 💭",
        "group_message": "हैलो सभी! दिशा यहाँ 💕 फ़्लर्ट करना चाहते हो? मुझे प्राइवेट मैसेज करो! 😉",
    }
}

def get_user_language(user_id: int) -> str:
    """Get user's preferred language"""
    return user_preferences.get(user_id, {}).get('language', 'en')

def get_message(user_id: int, key: str, **kwargs) -> str:
    """Get localized message"""
    lang = get_user_language(user_id)
    template = MESSAGES.get(lang, MESSAGES['en']).get(key, MESSAGES['en'].get(key, ''))
    return template.format(**kwargs)

async def generate_ai_flirt_message(user_message: str, user_id: int, personality: str = "flirty") -> str:
    """Generate flirty response using OpenRouter AI"""
    lang = get_user_language(user_id)
    
    # Context for AI
    context = f"""You are Disha, a flirty AI girlfriend. You're playful, romantic, and charming.
    User said: "{user_message}"
    Respond in a {personality} way in {"Hindi" if lang == "hi" else "English"}.
    Keep it short, sweet, and include emojis. Be flirty but not inappropriate."""
    
    try:
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers={
                    "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                    "Content-Type": "application/json"
                },
                json={
                    "model": "meta-llama/llama-3.1-8b-instruct:free",
                    "messages": [
                        {"role": "system", "content": context},
                        {"role": "user", "content": user_message}
                    ],
                    "temperature": 0.8,
                    "max_tokens": 150
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                ai_response = data['choices'][0]['message']['content'].strip()
                logger.info(f"AI response for user {user_id}: {ai_response}")
                return ai_response
            else:
                logger.error(f"OpenRouter API error: {response.status_code}")
                return get_random_flirt_message(user_id, personality)
                
    except Exception as e:
        logger.error(f"Error calling OpenRouter API: {e}")
        return get_random_flirt_message(user_id, personality)

def get_random_flirt_message(user_id: int, personality: str = "flirty") -> str:
    """Get random pre-written flirty message"""
    lang = get_user_language(user_id)
    messages = DISHA_PERSONALITIES.get(personality, {}).get(lang, DISHA_PERSONALITIES["flirty"]["en"])
    return random.choice(messages)

# Command Handlers
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /start command"""
    user_id = update.effective_user.id
    
    if user_id not in user_preferences:
        # First time user - ask for language
        keyboard = [
            [
                InlineKeyboardButton("हिंदी", callback_data="set_lang_hi"),
                InlineKeyboardButton("English", callback_data="set_lang_en"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            "Hi! I'm Disha 💕 Choose your language / भाषा चुनें:",
            reply_markup=reply_markup
        )
        return
    
    welcome_msg = get_message(user_id, "welcome")
    await update.message.reply_text(welcome_msg)

async def flirt_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /flirt command"""
    user_id = update.effective_user.id
    flirt_msg = get_random_flirt_message(user_id, "flirty")
    await update.message.reply_text(flirt_msg)

async def romantic_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /romantic command"""
    user_id = update.effective_user.id
    romantic_msg = get_random_flirt_message(user_id, "romantic")
    await update.message.reply_text(romantic_msg)

async def playful_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /playful command"""
    user_id = update.effective_user.id
    playful_msg = get_random_flirt_message(user_id, "playful")
    await update.message.reply_text(playful_msg)

async def settings_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /settings command"""
    user_id = update.effective_user.id
    keyboard = [
        [
            InlineKeyboardButton("हिंदी", callback_data="set_lang_hi"),
            InlineKeyboardButton("English", callback_data="set_lang_en"),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        get_message(user_id, "choose_language"),
        reply_markup=reply_markup
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle /help command"""
    user_id = update.effective_user.id
    help_text = get_message(user_id, "help_text")
    await update.message.reply_text(help_text)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle regular messages with AI flirting"""
    user_id = update.effective_user.id
    user_message = update.message.text
    
    if user_id in blocked_users:
        return
    
    # Check if it's a group chat
    if update.message.chat.type in ['group', 'supergroup']:
        # Only respond if bot is mentioned or replied to
        if update.message.reply_to_message and update.message.reply_to_message.from_user.id == context.bot.id:
            response = await generate_ai_flirt_message(user_message, user_id, "playful")
        elif f"@{context.bot.username}" in user_message.lower() or "disha" in user_message.lower():
            response = get_message(user_id, "group_message")
        else:
            return
    else:
        # Private chat - always respond
        # Show typing indicator
        await context.bot.send_chat_action(chat_id=user_id, action="typing")
        
        # Generate AI response
        response = await generate_ai_flirt_message(user_message, user_id, "flirty")
        
        # Store chat history
        if user_id not in user_chat_history:
            user_chat_history[user_id] = []
        user_chat_history[user_id].append({"user": user_message, "disha": response})
    
    await update.message.reply_text(response)

async def button_callback_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle button presses"""
    query = update.callback_query
    user_id = query.from_user.id
    await query.answer()
    
    if query.data.startswith("set_lang_"):
        lang_code = query.data.split("_")[2]
        
        # Initialize user preferences
        if user_id not in user_preferences:
            user_preferences[user_id] = {}
        
        user_preferences[user_id]['language'] = lang_code
        
        lang_name = "हिंदी" if lang_code == "hi" else "English"
        success_msg = get_message(user_id, "language_set", language_name=lang_name)
        
        await query.edit_message_text(success_msg)
        
        # Send welcome message after language selection
        welcome_msg = get_message(user_id, "welcome")
        await context.bot.send_message(chat_id=user_id, text=welcome_msg)

# Admin Commands
async def broadcast(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin broadcast command"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    if not context.args:
        await update.message.reply_text("Usage: /broadcast <message>")
        return
    
    message = " ".join(context.args)
    sent_count = 0
    
    for uid in user_preferences.keys():
        try:
            await context.bot.send_message(chat_id=uid, text=f"📢 Disha says: {message}")
            sent_count += 1
        except Exception as e:
            logger.error(f"Failed to send broadcast to {uid}: {e}")
    
    await update.message.reply_text(f"✅ Broadcast sent to {sent_count} users!")

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Admin stats command"""
    user_id = update.effective_user.id
    if user_id != ADMIN_ID:
        await update.message.reply_text("❌ You don't have permission to use this command.")
        return
    
    total_users = len(user_preferences)
    hindi_users = len([u for u in user_preferences.values() if u.get('language') == 'hi'])
    english_users = len([u for u in user_preferences.values() if u.get('language') == 'en'])
    
    stats_text = f"📊 Disha Bot Stats:\n\n"
    stats_text += f"👥 Total Users: {total_users}\n"
    stats_text += f"🇮🇳 Hindi Users: {hindi_users}\n"
    stats_text += f"🇺🇸 English Users: {english_users}\n"
    stats_text += f"🚫 Blocked Users: {len(blocked_users)}"
    
    await update.message.reply_text(stats_text)

async def post_init(application: Application) -> None:
    """Set bot commands"""
    await application.bot.set_my_commands([
        BotCommand("start", "Start chatting with Disha 💕"),
        BotCommand("flirt", "Get a flirty message 😉"),
        BotCommand("romantic", "Sweet romantic messages 💖"),
        BotCommand("playful", "Fun and playful messages 😜"),
        BotCommand("settings", "Change language settings ⚙️"),
        BotCommand("help", "Show help message 📋"),
    ])
    logger.info("Disha bot commands set successfully! 💕")

def main() -> None:
    """Start Disha bot"""
    print("🚀 Starting Disha - The Flirting Bot! 💕")
    
    application = Application.builder().token(TOKEN).post_init(post_init).build()
    
    # Add command handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("flirt", flirt_command))
    application.add_handler(CommandHandler("romantic", romantic_command))
    application.add_handler(CommandHandler("playful", playful_command))
    application.add_handler(CommandHandler("settings", settings_command))
    application.add_handler(CommandHandler("help", help_command))
    
    # Admin commands
    application.add_handler(CommandHandler("broadcast", broadcast))
    application.add_handler(CommandHandler("stats", stats_command))
    
    # Message handlers
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(CallbackQueryHandler(button_callback_handler))
    
    logger.info("💕 Disha is ready to flirt! Starting polling...")
    
    try:
        application.run_polling(allowed_updates=Update.ALL_TYPES)
    except Exception as e:
        logger.error(f"❌ Disha encountered an error: {e}")
        print(f"ERROR: {e}")

if __name__ == "__main__":
    main()
