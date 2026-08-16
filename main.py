from bot.bot import run_bot
from bot.app import run_app, build_app

import threading

if __name__ == "__main__":
    discord_thread = threading.Thread(target=run_bot, daemon=True)
    discord_thread.start()

    run_app(build_app())