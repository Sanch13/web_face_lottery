import logging
import time
from datetime import datetime, date, timedelta

from celery.app import shared_task
from django.conf import settings
from email.message import EmailMessage

from post.services.json_parse_birthday_service import JsonImportService
from post.services.seq_tg_post_service import SequentialPostService
from post.utils import send_message, send_post_to_tg_channel

logger = logging.getLogger('celery_tasks')


@shared_task
def send_admin_email(text=None):
    logger.info("---------Start---------send_admin_email()---------")
    try:
        text_body = text or f'TG POST {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}'
        message = EmailMessage()
        message['Subject'] = 'TG POST'
        message['From'] = settings.SENDER_EMAIL
        message['To'] = settings.ADMIN_EMAIL
        message.set_content(text_body)

        send_message(message=message)

        logger.info("Email успешно отправлен админу")
        logger.info("---------End---------send_admin_email()---------")
    except Exception as e:
        logger.exception(f"Ошибка: {e}")


@shared_task
def send_post_to_tg():
    start_time = time.time()
    logger.info(f'Отправка ТГ поста в ТГ канал')
    try:
        success = send_post_to_tg_channel()
        if success:
            logger.info(f'Затраченное время на отправку составило {time.time() - start_time:.2f} секунд.')
        else:
            msg = f"По каким-то причинам не смог отправить пост в ТГ. Статус отправки поста:{success}"
            logger.info(msg)
            send_admin_email(text=msg)
    except Exception as e:
        logger.exception(f"Неожиданная ошибка: {str(e)}")


@shared_task
def import_birthday_person_from_json():
    start_time = time.time()
    logger.info(f'Чтение данных из json')
    try:
        json_service = JsonImportService()
        json_service.import_birthday_data()
        json_service.cleanup_file()
        logger.info(f'Затраченное время на импорт из json составило {time.time() - start_time:.2f} секунд.')
    except Exception as e:
        logger.exception(f"Неожиданная ошибка: {e}")


@shared_task
def generate_or_update_weekly_posts():
    """
    Генерация или ОБНОВЛЕНИЕ постов на 7 дней вперед
    (только при изменении количества именинников)
    """
    seq_service = SequentialPostService()
    now = date.today()
    results = []
    start_time = time.time()

    logger.info(f"🔄 Начало обновления постов на 7 дней с {now}")

    for i in range(7):
        target_date = now + timedelta(days=i)

        message = seq_service.generate_or_update_post_for_date(target_date)

        if message:
            if "актуален" in message:
                status = "⏭️"
            elif "обновлен" in message:
                status = "🔄"
            else:
                status = "✅"
            results.append(f"{status} {target_date}: {message}")
        else:
            results.append(f"❌ {target_date}: ")

    final_result = "\n".join(results)
    logger.info(f"🏁 Обновление постов завершено:\n{final_result}")
    logger.info(f'Затраченное время составило {time.time() - start_time:.2f} секунд.')

