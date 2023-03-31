import json
import os

from telegram.ext import CommandHandler, MessageHandler, filters, ApplicationBuilder, CallbackQueryHandler

from src.routs import *
from src.routs_for_ordering import *


def main():
    token = os.environ.get('BOT_TOKEN')
    with open('resources/bar.json') as f:
        bar = json.load(f)
    application = ApplicationBuilder().token(token).build()

    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help))
    application.add_handler(MessageHandler(filters.TEXT, shift_started))
    application.add_handler(MessageHandler(filters.TEXT, unknown_text))
    application.add_handler(CallbackQueryHandler(button))

    application.bot_data['bar'] = bar
    application.run_polling()


if __name__ == '__main__':
    main()
