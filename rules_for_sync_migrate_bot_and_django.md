# 1. Локально обновить таблицы через alembic в bot-service

```shell
(.venv) user@pc:~/Projects/bots/reg-user-bot-miran$ alembic revision --autogenerate -m "add date_joined column"
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.ddl.postgresql] Detected sequence named 'lotteries_id_seq' as owned by integer column 'lotteries(id)', assuming SERIAL and omitting
INFO  [alembic.ddl.postgresql] Detected sequence named 'tickets_id_seq' as owned by integer column 'tickets(id)', assuming SERIAL and omitting
INFO  [alembic.autogenerate.compare] Detected added column 'users.date_joined'
  Generating /home/user/Projects/bots/reg-user-bot-miran/alembic/versions/12980778e8c8_add_date_joined_column.py ...  done
(.venv) user@pc:~/Projects/bots/reg-user-bot-miran$ alembic upgrade head
INFO  [alembic.runtime.migration] Context impl PostgresqlImpl.
INFO  [alembic.runtime.migration] Will assume transactional DDL.
INFO  [alembic.runtime.migration] Running upgrade c4a61144b3cf -> 12980778e8c8, add date_joined column
```

# 2. Локально обновить пустую миграцию в django-service и запустить миграцию в нужную БД (обновятся метаданные)

```shell
(.venv) user@pc:~/Projects/webFaceLottery$ python manage.py makemigrations webfacetg --empty --name add_date_joined_metadata
Migrations for 'webfacetg':
  webfacetg/migrations/0002_add_date_joined_metadata.py
(.venv) user@pc:~/Projects/webFaceLottery$ python manage.py migrate webfacetg --database=psql
Operations to perform:
  Apply all migrations: webfacetg
Running migrations:
  Applying webfacetg.0002_add_date_joined_metadata... OK
(.venv) user@pc:~/Projects/webFaceLottery$ python manage.py shell
Python 3.11.14 (main, Oct 10 2025, 08:54:03) [GCC 11.4.0] on linux
Type "help", "copyright", "credits" or "license" for more information.
(InteractiveConsole)
>>> from webfacetg.models import TelegramUser
>>> 
>>> # 1. Проверить что поле доступно
>>> user = TelegramUser.objects.using('psql').first()
>>> print(f"User: {user.full_name}, Date joined: {user.date_joined}")
User: Пушкин Александр Сергеевич, Date joined: 2025-11-13 09:20:45.228441
>>> print(TelegramUser._meta.get_field('date_joined'))
webfacetg.TelegramUser.date_joined
```
---

### Server side

# Скопировать файлы миграции и измененных моделей
# 1. Остановить бота
sudo systemctl stop telegram-bot
# 2. Применить Alembic миграцию
cd /path/to/bot
alembic upgrade head


# Скопировать файлы миграции и измененных моделей
# 1. Остановить Django
sudo systemctl stop Django
# 2. Применить Django миграцию  
cd /path/to/django
python manage.py migrate webfacetg --database=psql
# 3. Проверить
python manage.py showmigrations webfacetg --database=psql
# 4. Проверить новые колонки в shell
python manage.py shell


# 1. Запустить бота
sudo systemctl start telegram-bot

# 2. Запустить Django
sudo systemctl start Django
