import os

from celery import Celery
from celery.schedules import crontab

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

app = Celery("tg_post")
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()

# Настройка периодических задач
app.conf.beat_schedule = {
    'send_admin_email': {
        'task': 'post.tasks.send_admin_email',
        'schedule': crontab(hour=10, minute=57, day_of_week='*'),
    },
    'import_birthday_person_from_json': {
        'task': 'post.tasks.import_birthday_person_from_json',
        'schedule': crontab(hour=5, minute=5, day_of_week='*'),
    },
    'generate_or_update_weekly_posts': {
        'task': 'post.tasks.generate_or_update_weekly_posts',
        'schedule': crontab(hour=5, minute=15, day_of_week='*'),
    },
    'send_post_to_tg': {
        'task': 'post.tasks.send_post_to_tg',
        'schedule': crontab(hour=8, minute=30, day_of_week='*'),
    },
    'cleanup_old_posts_only': {
        'task': 'post.tasks.cleanup_old_posts_only',
        'schedule': crontab(hour=2, minute=30, day_of_week='*'),
    },
    'cleanup_old_birthdays_only': {
        'task': 'post.tasks.cleanup_old_birthdays_only',
        'schedule': crontab(hour=3, minute=30, day_of_week='*'),
    },
}
