from flask import Flask
from threading import Thread
import time
import requests
import os

app = Flask(__name__)

@app.route('/')
def home():
    return """
    <html>
    <head><title>Telegram Bot Status</title></head>
    <body style="font-family: Arial; text-align: center; padding: 50px;">
        <h1>🤖 Anonymous Telegram Bot</h1>
        <h2 style="color: green;">✅ Bot is Running!</h2>
        <p>Your bot is live and processing messages 24/7</p>
        <p><strong>Repository:</strong> <a href="https://github.com/FLASHANISH/anonymous-chat-bot">GitHub</a></p>
        <p><strong>Uptime:</strong> <span id="uptime"></span></p>
        <script>
            setInterval(() => {
                document.getElementById('uptime').innerText = new Date().toLocaleString();
            }, 1000);
        </script>
    </body>
    </html>
    """

@app.route('/status')
def status():
    return {"status": "online", "message": "Bot is running successfully", "timestamp": time.time()}

@app.route('/ping')
def ping():
    return "pong"

def run():
    app.run(host='0.0.0.0', port=8080, debug=False, threaded=True)

def keep_alive():
    t = Thread(target=run)
    t.daemon = True
    t.start()
    
    # Self-ping to keep alive
    def self_ping():
        while True:
            try:
                time.sleep(300)  # Ping every 5 minutes
                requests.get("http://localhost:8080/ping", timeout=10)
            except:
                pass
    
    ping_thread = Thread(target=self_ping)
    ping_thread.daemon = True
    ping_thread.start()
