# 🤖 Anonymous Telegram Chat Bot

A feature-rich Telegram bot that enables anonymous chatting between users with multi-language support (Hindi/English) and advanced moderation features.

## 🚀 Features

- **Anonymous Chat**: Connect random users for private conversations
- **Multi-language Support**: Full Hindi and English language support
- **Content Filtering**: Blocks inappropriate links and usernames
- **Admin Controls**: Broadcast messages, block/unblock users, handle reports
- **Smart Queue System**: Intelligent user matching algorithm
- **Interactive UI**: Inline keyboards for better user experience
- **24/7 Operation**: Designed for continuous deployment on various platforms
- **Keep-Alive System**: Built-in web server for Replit/hosting platforms

## 🛠️ Tech Stack

- **Python 3.11+**
- **python-telegram-bot 22.3** - Modern async Telegram bot framework
- **Flask** - Web server for keep-alive functionality
- **Async/Await** - High performance asynchronous operations
- **Advanced Logging** - Comprehensive monitoring and debugging

## 📦 Deployment

### One-Click Deploy

[![Deploy to Render](https://render.com/images/deploy-to-render-button.svg)](https://render.com/deploy?repo=https://github.com/FLASHANISH/telegram-anonymous-bot)

[![Deploy on Railway](https://railway.app/button.svg)](https://railway.app/template/DLlHxL?referralCode=alphasec)

### Manual Deploy on Render.com

1. **Service Type**: Background Worker (NOT Web Service)
2. **Build Command**: `pip install -r requirements.txt`
3. **Start Command**: `python python.py`
4. **Environment Variable**: 
   - Key: `TELEGRAM_BOT_TOKEN`
   - Value: Your bot token from @BotFather

### Deploy on Railway/Heroku

Use the included `Procfile` and `requirements.txt`

## 🎯 Commands

- `/start` - Start the bot and join chat queue
- `/stop` - End current chat
- `/next` - Find new chat partner
- `/help` - Show all commands
- `/settings` - Change language preferences
- `/report <chat_id>` - Report inappropriate behavior

## ⚙️ Configuration

Set your bot token as environment variable:
```
TELEGRAM_BOT_TOKEN=your_token_here
```

## 🤝 Contributing

Feel free to submit issues and pull requests!

---

**⚠️ Important: This is a BACKGROUND WORKER application, not a web service!**
