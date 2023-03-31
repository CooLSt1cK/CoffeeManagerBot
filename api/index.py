from threading import Thread

from flask import Flask

from main import main

app = Flask(__name__)

global bot_thread


@app.route('/start')
def start():
    try:
        global bot_thread
        bot_thread = Thread(target=main)
        bot_thread.start()
        return str(bot_thread.is_alive())
    except Exception as e:
        return str(e.__traceback__)
