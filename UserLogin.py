from flask_login import LoginManager, login_required, logout_user
from app_create import app
from flask import redirect, url_for
from models import DataBase
db = DataBase()


class UserLogin:
    def fromDB(self, user_id):
        self.__user = db.get_user_by_id(user_id)
        return self

    def get_user(self):
        try:
            return self.__user
        except:
            return None

    def create(self, user):
        self.__user = user
        return self

    def is_authenticated(self):
        return True

    def is_active(self):
        return True

    def is_anonymous(self):
        return False

    def get_id(self):
        id_user = self.__user[0]
        return id_user


login_manager = LoginManager(app)


@login_manager.user_loader
def load_user(user_id):
    return UserLogin().fromDB(user_id)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect("/")
