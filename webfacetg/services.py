from datetime import datetime

from django.db import IntegrityError, DatabaseError

from .models import Lottery


def add_lottery(name, description, is_active) -> None:
    try:
        Lottery.objects.using("psql").create(
            name=name,
            description=description,
            is_active=is_active,
            create=datetime.now()
        )
    except IntegrityError as e:
        print(f"IntegrityError: {e}")
    except DatabaseError as e:
        print(f"DatabaseError: {e}")

# TODO: Why? Delete maybe?
# def add_user(telegram_id, full_name, full_name_from_tg, username):
#     try:
#         TelegramUser.objects.using("psql").create(
#             telegram_id=telegram_id,
#             full_name=full_name,
#             full_name_from_tg=full_name_from_tg,
#             username=username,
#             is_active=True,
#         )
#     except IntegrityError as e:
#         print(f"IntegrityError: {e}")
#     except DatabaseError as e:
#         print(f"DatabaseError: {e}")
