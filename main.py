# This is the main entry point for Replit
import os
import sys
import time
import traceback

# Add the current directory to Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Import and run the bot
from python import main

def run_with_restart():
    """Run the bot with automatic restart on crash"""
    while True:
        try:
            print("🤖 Starting Anonymous Telegram Bot on Replit...")
            main()
        except KeyboardInterrupt:
            print("\n⏹️ Bot stopped by user")
            break
        except Exception as e:
            print(f"❌ Bot crashed with error: {e}")
            print("📋 Full traceback:")
            traceback.print_exc()
            print("🔄 Restarting bot in 10 seconds...")
            time.sleep(10)
        except SystemExit:
            print("🛑 Bot exited")
            break

if __name__ == "__main__":
    run_with_restart()
