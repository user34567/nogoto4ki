from flask import Flask
from config import config_app

app = Flask(__name__)
config_app(app)
