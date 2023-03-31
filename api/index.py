from flask import Flask
from main import main

app = Flask(__name__)


@app.route('/')
def home():
    main()
    return 'Hello, World!'


@app.route('/about')
def about():
    return 'About'
