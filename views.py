from app_create import app
from flask import request, flash
from flask_login import login_required
from controll import *

@app.route('/')
def index():
    return index_func()


@app.route("/profile")
@app.route("/profile/<int:id_user>")
def profile(id_user=None):
    return profile_func(id_user)


@app.route('/register', methods=['POST', 'GET'])
def register():
    if request.method == "POST":
        email = request.form["email"]
        nickname = request.form["nickname"]
        password = request.form["password"]
        return register_func(email, nickname, password)
    return render_template("register.html")


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == "POST":
        email = request.form['email']
        password = request.form['password']
        return login_func(email, password)
    return render_template("login.html")


@app.route("/createpost", methods=['POST', 'GET'])
@login_required
def create_post():
    if request.method == "GET":
        return render_template("createpost.html")
    if 'image' not in request.files:
        flash('No file part')
        return redirect(request.url)
    about = request.form['about']
    images = request.files.getlist('image')
    return create_post_func(images, about)


@app.route("/setavatar", methods=['POST', 'GET'])
@login_required
def set_avatar():
    if request.method == "GET":
        return render_template("setavatar.html")
    if 'image' not in request.files:
        flash('No file part')
        return redirect(request.url)
    image = request.files['image']
    return set_avatar_func(image)


@app.route("/posts")
@app.route("/posts/<int:id_user>")
@login_required
def posts(id_user=None):
    redirect("/posts")
    return show_posts(id_user)


@app.route("/post/<int:id_post>")
def post(id_post):
    return get_post(id_post)


@app.route("/like/<int:id_post>")
@login_required
def like(id_post):
    return like_func(id_post)


@app.route("/dislike/<int:id_post>")
@login_required
def dislike(id_post):
    return dislike_func(id_post)


@app.route("/subscribes/<int:id_user>", methods=['GET', 'POST'])
@login_required
def subscribes(id_user):
    if request.method == "POST":
        search = request.form['search']
        print("search ",search)
        return subscribes_func(search=search)
    else:
        return subscribes_func(id_user=id_user)


@app.route("/subscribers/<int:id_user>", methods=['GET', 'POST'])
@login_required
def subscribers(id_user):
    if request.method == "POST":
        search = request.form['search']
        print("search ",search)
        return subscribes_func(search=search)
    else:
        return subscribers_func(id_user=id_user)




@app.route('/accept/<int:id_user>/<string:nickname>')
def accept(id_user,nickname):
    try:
        reg_user = db.pop_reg_user_by_id(id_user)
        db.insert_user()
        email = reg_user[0]
        password = reg_user[1]
        db.insert_user(id_user, nickname, email, password)
        return redirect("/login")
    except Exception as e:
        print(e)
        return render_template("error.html")


@app.route('/sub/<int:id_user1>/<int:id_user2>/<string:func>')
def subscribe(id_user1, id_user2, func):
    return subscribe_func(id_user1, id_user2, func)