from flask import render_template
from codeReader import app
from codeReader.email import send_email


def send_lead_notification_email(data):
    send_email('Error MEssage', sender=app.config['ADMINS'], recipients=app.config['ADMINS'].split(), text_body=render_template(
        'email/lead_notification.txt'), html_body=render_template('email/lead_notification.html'))
