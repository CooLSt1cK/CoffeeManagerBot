from threading import Thread

from flask import Flask
from main import main

app = Flask(__name__)

global bot_thread


@app.route('/start')
def start():
    bot_thread = Thread(target=main, daemon=True)
    bot_thread.start()
    return 'Bot is started'


@app.route('/stop')
def stop():
    if bot_thread:
        bot_thread.join()
        return 'Bot is stopped'
    else:
        return 'Bot has not ran yet'
