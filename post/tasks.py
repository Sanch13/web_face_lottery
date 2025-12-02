import os
import time
import logging
from email.message import EmailMessage
from datetime import datetime, date, timedelta

from django.conf import settings
from django.utils import timezone

from celery.app import shared_task
from post.services.json_parse_birthday_service import JsonImportService
from post.services.seq_tg_post_service import SequentialPostService
from post.utils import send_message, send_post_to_tg_channel
from post.models import TelegramPost, BirthdayPerson

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
def import_birthday_person_from_json():
    start_time = time.time()
    logger.info(f'Чтение данных из json')
    try:
        json_service = JsonImportService()
        result = json_service.import_birthday_data()

        if result is False:
            error_msg = f"Файл JSON не найден: {settings.PATH_TO_JSON_FILE}"
            logger.warning(error_msg)

            return {
                "status": "skipped",
                "message": error_msg,
                "file_exists": os.path.exists(settings.PATH_TO_JSON_FILE)
            }

        success, error, _ = result

        if success > 0:
            json_service.cleanup_file()
            logger.info(f"🗑️ Файл удален после успешного импорта {success} записей")
        else:
            logger.warning(f"⚠️ Файл НЕ удален: импортировано 0 записей, ошибок: {error}")

        logger.info(
            f'Импорт завершен (Успех: {success}, Ошибки: {error}). '
            f'Затраченное время: {time.time() - start_time:.2f} секунд.'
        )

        return {
            "status": "success",
            "imported": success,
            "errors": error,
            "file_deleted": success > 0
        }

    except Exception as e:
        logger.exception(f"Неожиданная ошибка: {e}")
        raise


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


@shared_task
def send_post_to_tg():
    start_time = time.time()
    logger.info(f'Отправка ТГ поста в ТГ канал')
    try:
        success = send_post_to_tg_channel()
        if success:
            logger.info(
                f'Затраченное время на отправку составило {time.time() - start_time:.2f} секунд.')
        else:
            msg = f"По каким-то причинам не смог отправить пост в ТГ. Статус отправки поста:{success}"
            logger.info(msg)
            send_admin_email(text=msg)
    except Exception as e:
        logger.exception(f"Неожиданная ошибка: {str(e)}")


@shared_task
def cleanup_old_posts_only():
    """
    Удаляет только Telegram посты недельной давности
    """
    start_time = time.time()
    logger.info(f"Удаляю посты недельной давности")
    try:
        week_ago = timezone.localtime().now() - timedelta(days=7)

        deleted_count = TelegramPost.objects.filter(
            post_date__lt=week_ago
        ).delete()[0]
        data = {
            'status': 'success',
            'deleted_posts': deleted_count,
            'cleanup_date': timezone.localtime().now().isoformat()
        }
        logger.info(f"Удаление постов завершено: data: {data}")
        logger.info(f'Затраченное время составило {time.time() - start_time:.2f} секунд.')
        return data

    except Exception as e:
        logger.exception(f"Ошибка при удалении недельной постов: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }


@shared_task
def cleanup_old_birthdays_only():
    """
    Удаляет только именинников недельной давности
    """
    start_time = time.time()
    logger.info(f"Удаляю именинников недельной давности")
    try:
        week_ago = timezone.localtime().now() - timedelta(days=7)

        deleted_count = BirthdayPerson.objects.filter(
            import_date__lt=week_ago.date()
        ).delete()[0]
        data = {
            'status': 'success',
            'deleted_birthdays': deleted_count,
            'cleanup_date': timezone.localtime().now().isoformat()
        }
        logger.info(f"Удаление именинников недельной давности завершено: data: {data}")
        logger.info(f'Затраченное время составило {time.time() - start_time:.2f} секунд.')
        return data

    except Exception as e:
        logger.exception(f"Ошибка при удалении именинников недельной давности: {e}")
        return {
            'status': 'error',
            'error': str(e)
        }
