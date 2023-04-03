import asyncio
import json
import logging
import os

from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder, CallbackQueryHandler

from src.routs import *
from src.routs_for_ordering import *

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO,
    filename='logs.txt',
    filemode='w+'
)


def main():
    token = os.environ.get('BOT_TOKEN')
    with open('resources/menu.json') as f:
        bar = json.load(f)
    asyncio.set_event_loop(asyncio.new_event_loop())
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(MessageHandler(filters.TEXT, shift_started))
    application.add_handler(MessageHandler(filters.TEXT, unknown_text))
    application.add_handler(CallbackQueryHandler(button))

    application.bot_data['menu'] = bar
    application.run_polling()


if __name__ == '__main__':
    main()
