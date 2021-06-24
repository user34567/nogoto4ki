from flask import render_template
from models import db
from hashlib import sha256
from UserLogin import UserLogin
from flask_login import login_user, current_user
from flask import redirect, url_for
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash
from random import randint
from emailapp import send_defaul_msg
from const import POSTS_URL, AVATARS_URL



def register_func(email, nickname, password):
    message_password = password
    if nickname == '':
        nickname = "user"
    password = (sha256(password.encode('utf-8')).hexdigest())[0:120]
    if db.get_user_by_email(email) is not None:
        return render_template("register.html", mes="this email is already taken")
    if db.get_user_by_password(password) is not None:
        return render_template("register.html", mes="this password is already taken")
    successful = db.insert_user_to_register_users(email, password)
    #
    if successful:

        id_user = db.get_id_reg_user_by_email_password(email, password)
        successful = send_defaul_msg(id_user, nickname, email)
        if successful :
            return "<h1>Accept from email</h1>"
        return f"""
        <h1>Ошибка отправки подтверждения на почту. Подтвердите регистрацию нажав на "ACCEPT"</h1>
        <br>
        <br>
    <a href='https://nogoto4ki.herokuapp.com/accept/{id_user}/{nickname}'>
        <h1>ACCEPT</h1>
    </a>"""
    return render_template('error.html')


def login_func(email, password):
    password = (sha256(password.encode('utf-8')).hexdigest())[0:120]
    print(password)
    user = db.get_user_by_email_password(email, password)
    if user is None:
        return render_template("login.html", mes="password or email is not correct")
    user = UserLogin().create(user)
    login_user(user)
    return redirect("/")


def get_ava(ava_path):
    if ava_path is None:
        return "static/avatars/img.png"
    else:
        return 'https://nogoto4ki.herokuapp.com/static/avatars/' + ava_path


def set_avatar_func(file):
    if file is None:
        return redirect('/profile')
    try:
        id_user = current_user.get_id()
        fname = ((sha256(str(id_user).encode('utf-8')).hexdigest() + secure_filename(file.filename))[-120:-1])
        file.save("{path}/{fname}".format(path=AVATARS_URL,fname=fname))
        db.set_avatar(id_user, fname)
        return redirect('/profile')
    except Exception as e:
        print(e)
        return render_template("error.html")


def create_post_func(images, about):
    if images is None:
        return redirect('/createpost')
    file_names = []
    id_user = current_user.get_id()
    for i in range(len(images)):
        file_names.append((sha256(str(id_user).encode('utf-8')).hexdigest() + secure_filename(images[i].filename))[-119:-1])
    successful = db.insert_post(id_user, about)
    if not successful:
        return render_template("error.html")
    id_post = db.get_last_user_post_id(id_user)
    i = 0
    for file_name in file_names:
        successful = db.insert_post_photo(id_post, file_name)
        print(successful)
        while not successful:
            if len(list(file_name)) > 119:
                file_name = file_name[-100:-1]
            file_name = str(randint(0,9))+file_name
            successful = db.insert_post_photo(id_post, file_name)
        images[i].save("{path}/{file_name}".format(path=POSTS_URL, file_name=file_name))
        i = i + 1
    return redirect('/profile')


def show_posts(id_user):
    if id_user is None:
        id_user = current_user.get_id()
    posts = db.get_user_posts(id_user)  # id_post/date/likes/dislikes/img
    return render_template("posts.html",  header=get_header(), posts=posts)


def get_likes(id_post):
    likes = []
    if db.get_like(id_post, current_user.get_id()) is None:
        likes.append("https://nogoto4ki.herokuapp.com/static/staticimg/none.png")
    else:
        likes.append("https://nogoto4ki.herokuapp.com/static/staticimg/like.png")
    if db.get_dislike(id_post, current_user.get_id()) is None:
        likes.append("https://nogoto4ki.herokuapp.com/static/staticimg/none.png")
    else:
        likes.append("https://nogoto4ki.herokuapp.com/static/staticimg/dislike.png")
    return likes


def get_post(id_post):
    current_user_id = current_user.get_id()
    db.delete_new(current_user_id,id_post)
    post = db.get_post_by_id(id_post)
    post_photos = db.get_post_photos(id_post)
    src_list = []
    print(post)
    likes = get_likes(id_post)
    for post_photo in post_photos:
        src_list.append("https://nogoto4ki.herokuapp.com/static/posts/" + post_photo[0])
    return render_template("post.html", post=post, src_list=src_list,  header=get_header(), likes=likes, counter=len(src_list), db=db, user_id=current_user_id)


def index_func():
    try:
        us_id = current_user.get_id()
    except:
        us_id = None
    posts = db.get_posts()
    return render_template("index.html", header=get_header(us_id), posts=posts, count=len(posts)//4)


def get_header(id_user=1):
    if id_user is None:
        return {"a_href": "/login",
                "a_name": "Login",
                "news": []}
    user = current_user.get_user()
    name = user[1]
    if len(list(name)) > 5:
        name = name[0:5] + ".."
    return {"a_href": "/profile",
            "a_name": name,
            "news": get_news(user[0])}


def get_news(id_user):
    news = []
    news_from_db = db.get_news(id_user)
    for new in news_from_db:
        news.append({
            "src":" https://nogoto4ki.herokuapp.com/static/posts/{img_name}".format(img_name=new[1]),
            "href":"https://nogoto4ki.herokuapp.com/post/{id}".format(id=new[0])
        })
    return news


def profile_func(id_user):
    if id_user == current_user.get_id() or id_user is None:
        user = current_user.get_user()
        buttons = [{'href': '/setavatar', 'text': 'Изменить аватар'},
                   {'href': '/createpost', 'text': 'Новый пост'},
                   {'href': '/logout', 'text': 'Выйти'}]
    else:
        id_current_user = current_user.get_id()
        user = db.get_user_by_id(id_user)
        if db.if_subscribe(id_current_user,id_user) is None:
            text = 'Подписаться'
            func = "INSERT"
        else:
            text = "Отписаться"
            func = "DELETE"
        buttons = [{'href': f'/sub/{id_current_user}/{id_user}/{func}', 'text': text}]
    sub_info = db.get_sub_and_posts_count(id_user=user[0])
    data = {
        'buttons': buttons,
        "subscribers_count": sub_info[1],
        "subscribes_count": sub_info[0],
        "posts_count": sub_info[2],
        "imgpath": get_ava(user[4]),
        "username": user[1],
        'id': user[0]
    }
    return render_template("profile.html", data=data, header=get_header())


def like_func(id_post):
    db.like_post(id_post, current_user.get_id())
    return redirect(f'https://nogoto4ki.herokuapp.com/post/{id_post}')


def dislike_func(id_post):
    db.dislike_post(id_post, current_user.get_id())
    return redirect(f'https://nogoto4ki.herokuapp.com/post/{id_post}')


def subscribes_func(search=None, id_user=None):
    if id_user:
        subscribes = db.get_subscribes(id_user) # nickname /ava_path / id / both sub-bs / both sub-ers/
        print(subscribes)
        return render_template('subscribes.html', header=get_header(), users=subscribes)
    finds = db.search_in_users_by_name(search)
    return render_template('subscribes.html', header=get_header(), users=finds)


def subscribers_func(search=None, id_user=None):
    if id_user:
        subscribes = db.get_subscribers(id_user) # nickname /ava_path / id / both sub-bs / both sub-ers/
        print(subscribes)
        return render_template('subscribes.html', header=get_header(), users=subscribes)
    finds = db.search_in_users_by_name(search)
    return render_template('subscribes.html', header=get_header(), users=finds)


def subscribe_func(id_user1, id_user2, func):
    if func == "DELETE":
        db.delete_sub(id_user1, id_user2)
        return redirect('', 204)
    elif func == "INSERT":
        db.insert_sub(id_user1, id_user2)
        return redirect('', 204)
    else:
        return render_template("error.html")

