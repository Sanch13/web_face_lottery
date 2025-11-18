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
        'schedule': crontab(hour=10, minute=57, day_of_week='mon-fri'),
    },
    # 'generate-daily-posts': {
    #     'task': 'telegram.tasks.generate_daily_posts',
    #     'schedule': crontab(hour=9, minute=25, day_of_week='mon-fri'),
    # },
    #     'publish-scheduled-posts': {
    #         'task': 'telegram.tasks.publish_scheduled_posts',
    #         'schedule': crontab(hour=9, minute=25, day_of_week='mon-fri'),
    #     },
}

app.conf.timezone = 'Europe/Moscow'
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/0'
