from flask import current_app as app, render_template
from flask_mail import Message
from threading import Thread
from app.extensions import mail

def send_async_email(app, msg):
    with app.app_context():
        mail.send(msg)

def send_email(subject, sender, recipients, text_body, html_body):
    msg = Message(subject, sender=sender, recipients=recipients)
    msg.body = text_body
    msg.html = html_body
    Thread(target=send_async_email, args=(app._get_current_object(), msg)).start()

# send reset password link to user
def send_password_reset_email(user):
    token = user.get_reset_password_token(app.config['SECRET_KEY'])
    send_email('[Lineage] Reset Your Password',
               sender=app.config['ADMINS'],
               recipients=[user.email],
               text_body=render_template('email/reset_password.txt',
                                         user=user, token=token),
               html_body=render_template('email/reset_password.html',
                                         user=user, token=token))

def sendEmailVerificationLink(user):
        # get url
        url_root = request.url_root
        # create token to send to user via email for verification
        token = auth_s.dumps({"user_id": user.user_id})
        send_email('[Lineage] Verify Email',
               sender=app.config['ADMINS'],
               recipients=[user.email],
               text_body=render_template('email/verifyEmail.txt',
                                         link=f'{url_root}{token}',
                                         user=user),
               html_body=render_template('email/verifyEmail.html',
                                         link=f'{url_root}verify_email/{token}',
                                         user=user))
        flash(f'Verify your email. Link has been sent to {user.email}', 'success')
