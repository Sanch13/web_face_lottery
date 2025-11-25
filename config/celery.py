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
    # 'import_birthday_person_from_json': {
    #     'task': 'post.tasks.import_birthday_person_from_json',
    #     'schedule': crontab(hour=10, minute=26, day_of_week='mon-fri'),
    # },
    # 'generate_or_update_weekly_posts': {
    #     'task': 'post.tasks.generate_or_update_weekly_posts',
    #     'schedule': crontab(hour=10, minute=27, day_of_week='mon-fri'),
    # },
    # 'send_post_to_tg': {
    #     'task': 'post.tasks.send_post_to_tg',
    #     'schedule': crontab(hour=10, minute=28, day_of_week='mon-fri'),
    # },
}
# придумать таску на удаление месячных именинников

app.conf.timezone = 'Europe/Moscow'
app.conf.broker_url = 'redis://localhost:6379/0'
app.conf.result_backend = 'redis://localhost:6379/0'
