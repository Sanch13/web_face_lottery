from datetime import datetime

from celery.app import shared_task
from django.conf import settings
from email.message import EmailMessage

from post.utils import send_message


@shared_task
def send_admin_email():
    # logger.info("---------Start---------send_admin_email()---------")
    try:
        text_body = f'TG POST {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        message = EmailMessage()
        message['Subject'] = 'TG POST'
        message['From'] = settings.SENDER_EMAIL
        message['To'] = settings.ADMIN_EMAIL
        message.set_content(text_body)

        send_message(message=message)

        # logger.info("Email успешно отправлен админу")
        # logger.info("---------End---------send_admin_email()---------")
    except Exception as e:
        print(e)
        # logger.exception(f"Ошибка: {e}")
