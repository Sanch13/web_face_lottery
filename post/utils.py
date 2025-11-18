import smtplib
from email.message import Message
import ssl
from django.conf import settings


def send_message(message: Message):
    context = ssl.create_default_context()
    with smtplib.SMTP(settings.SMTP_SERVER, settings.PORT) as server:
        server.starttls(context=context)
        server.login(
            settings.SENDER_EMAIL,
            settings.PASSWORD
        )
        server.send_message(message)
