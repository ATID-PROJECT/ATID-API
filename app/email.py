import os

from flask import render_template
from flask_mail import Message, Mail

from dynaconf import settings

from .celery import celery
import os
from .__init__ import create_app

app = create_app()
mail = Mail(app)

#send async email
def send_email(recipient, subject, template, **kwargs):
    if "DISABLE_SEND_EMAIL" not in os.environ:
        send_email_async.delay(recipient, subject, template, **kwargs)

@celery.task
def send_email_async(recipient, subject, template, **kwargs):
    with app.app_context():
        msg = Message(
        settings['EMAIL_SUBJECT_PREFIX'] + ' ' + subject,
        sender=settings['EMAIL_SENDER'],
        recipients=[recipient])
        msg.body = render_template(template + '.txt', **kwargs)
        msg.html = render_template(template + '.html', **kwargs)
        """images is an array where images[i][0] = 'name of image' 
        and images[i][1]= 'path of image' """
        if 'images' in kwargs:
            for img in kwargs.get('images'):
                with app.open_resource(img[1]) as fp:
                    msg.attach(img[0], "image/jpg", fp.read())
        mail.send(msg)