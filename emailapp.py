from flask_mail import Mail, Message
from app_create import app





def send_defaul_msg(id_user, nickname, email):
    mail = Mail(app)
    msg = Message("Accept email", sender=app.config['MAIL_DEFAULT_SENDER'], recipients=[email])
    msg.body = 'text body'
    msg.html = f"""
    <a href='https://nogoto4ki.herokuapp.com/accept/{id_user}/{nickname}'>
        <h1>ACCEPT</h1>
    </a>
"""
    try:
        mail.send(msg)
        return True
    except:
        return False

