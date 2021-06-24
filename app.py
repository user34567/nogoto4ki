from app_create import app

from views import *

from models import DataBase
db = DataBase()


if __name__ == "__main__":
    app.run()


