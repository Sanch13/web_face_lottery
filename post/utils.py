import os
import re
import ssl
import smtplib
import logging
from email.message import Message
from datetime import date

import requests
from pytrovich.detector import PetrovichGenderDetector
from pytrovich.enums import NamePart, Case
from pytrovich.maker import PetrovichDeclinationMaker

from django.conf import settings
from django.utils import timezone

from post.models import TelegramPost

logger = logging.getLogger('post')


def send_message(message: Message):
    context = ssl.create_default_context()
    with smtplib.SMTP(settings.SMTP_SERVER, settings.PORT) as server:
        server.starttls(context=context)
        server.login(
            settings.SENDER_EMAIL,
            settings.PASSWORD
        )
        server.send_message(message)

    logger.info(f"Письмо успешно отправлено!")


def send_post_to_tg_channel():
    """
    Отправка поста в Telegram канал

    Args:
        media: объект MediaContent
        text: текст для подписи

    Returns:
        tuple: (success: bool, result: str or int)
    """
    bot_token = settings.TELEGRAM_API_TOKEN
    channel_id = settings.TELEGRAM_CHAT_ID

    now = date.today()
    target_date = now

    post = TelegramPost.objects.filter(
        post_date=target_date,
        status='scheduled'
    ).first()
    logger.info(f"Сегодняшний пост {post}")

    if post is None:
        return False

    media = post.media_content
    text = post.final_text or post.text_template.text

    logger.info(f"📤 Отправка поста в Telegram...")

    # Определяем endpoint по типу медиа
    endpoints = {
        'photo': 'sendPhoto',
        'animation': 'sendAnimation',
        'video': 'sendVideo',
    }

    if media.media_type not in endpoints:
        logger.error(f"❌ Неподдерживаемый тип медиа: {media.media_type}")
        return False

    url = f"https://api.telegram.org/bot{bot_token}/{endpoints[media.media_type]}"

    try:
        if not media.media_file:
            logger.error(f"❌ Медиа файл не прикреплен")
            return False

        if not os.path.exists(media.media_file.path):
            logger.error(f"❌ Файл не найден на сервере: {media.media_file.path}")
            return False

        # Читаем файл в бинарном режиме
        with open(media.media_file.path, 'rb') as file:
            file_content = file.read()

            # Проверяем размер файла (Telegram ограничения)
            file_size = len(file_content)
            max_size = 50 * 1024 * 1024  # 50MB для фото/GIF, 50MB для видео

            if file_size > max_size:
                logger.error(
                    f"❌ Файл слишком большой: {file_size / (1024 * 1024):.1f}MB > {max_size / (1024 * 1024)}MB")
                return False

            # Подготавливаем файл для отправки
            file_name = os.path.basename(media.media_file.name)
            files = {
                media.media_type: (file_name, file_content)
            }

        # Параметры запроса
        payload = {
            'chat_id': channel_id,
            'caption': text,
            'parse_mode': 'HTML'
        }

        # Отправка запроса
        logger.info(f" 📡 Отправка запроса к Telegram API...")
        response = requests.post(url, data=payload, files=files, timeout=60)
        response_data = response.json()

        # Обработка ответа
        if response_data.get('ok'):
            message_id = response_data['result']['message_id']
            logger.info(f"✅ Пост успешно отправлен! message_id: {message_id}")
            post.status = "published"
            post.published_at = timezone.now()
            post.save()
            return True
        else:
            post.status = 'failed'
            post.save()
            error_code = response_data.get('error_code', 'Unknown')
            error_msg = response_data.get('description', 'Unknown error')
            logger.info(f"❌ Ошибка Telegram API:")
            logger.info(f"   Код: {error_code}")
            logger.info(f"   Описание: {error_msg}")
            return False

    except requests.exceptions.Timeout as e:
        logger.exception(f"❌ Таймаут при отправке запроса к Telegram {e}")
        return False
    except requests.exceptions.ConnectionError as e:
        logger.exception(f"❌ Ошибка подключения к Telegram API {e}")
        return False
    except FileNotFoundError as e:
        logger.exception(f"❌ Файл не найден: {media.media_file.path} {e}")
        return False
    except Exception as e:
        logger.exception(f"❌ Неожиданная ошибка: {str(e)}")
        return False


def parse_emoji_and_format_people(template_text, people_data):
    """
    Универсальная функция для работы с разными форматами шаблонов
    """
    # Варианты паттернов для поиска
    patterns = [
        r'\{([^}]+)\}\s*\{FIO\}\s*\(\{Department\}\)',  # {🎉} {FIO} ({Department})
        r'\{emoji:([^}]+)\}',  # {emoji:🎉}
        r'#emoji\{([^}]+)\}',  # #emoji{🎉}
    ]

    emoji = "⭐"  # дефолтный эмодзи
    working_template = template_text

    # Ищем эмодзи в шаблоне
    for pattern in patterns:
        match = re.search(pattern, working_template)
        if match:
            emoji = match.group(1)
            # Заменяем найденный паттерн на {people}
            working_template = re.sub(pattern, "{people}", working_template, 1)
            break

    # Форматируем людей
    formatted_lines = []
    for person in people_data:
        fio = format_fio(person.get('fio', ''))
        department = person.get('department', '')
        position = person.get('position', '')

        if department == "РУКОВОДСТВО И ОТДЕЛЬНЫЕ РАБОТНИКИ":
            display_department = position if position else ""
        else:
            try:
                display_department = get_abr_department(department) if department else ""
            except Exception:
                display_department = department if department else ""

        if fio and display_department:
            line = f"{emoji} <b>{fio} ({display_department})</b>"
        elif fio:
            line = f"{emoji} <b>{fio}</b>"
        else:
            continue

        formatted_lines.append(line)

    formatted_people = "\n".join(formatted_lines)

    # Если в шаблоне не было {people}, добавляем его
    if "{people}" not in working_template:
        working_template += "\n\n{people}"

    final_text = working_template.replace("{people}", formatted_people)
    return final_text


def format_fio(fio: str):
    maker = PetrovichDeclinationMaker()
    detector = PetrovichGenderDetector()

    lastname, firstname, middlename = fio.split()

    gender = detector.detect(firstname=firstname, lastname=lastname, middlename=middlename)

    l = maker.make(NamePart.LASTNAME, gender, Case.ACCUSATIVE, lastname)
    f = maker.make(NamePart.FIRSTNAME, gender, Case.ACCUSATIVE, firstname)
    m = maker.make(NamePart.MIDDLENAME, gender, Case.ACCUSATIVE, middlename)

    return f"{l} {f} {m}"


def get_abr_department(key):
    departments = {
        "АДМИНИСТРАТИВНО-ХОЗЯЙСТВЕННЫЙ ОТДЕЛ": "АХО",
        "БУХГАЛТЕРИЯ": "БУХ",
        "ВК ПРОИЗВОДСТВО": "ВК ПРОИЗВОДСТВО",
        "ВК СКЛАД ПОЛУФАБРИКАТОВ": "ВК СКЛАД",
        "ВК СКЛАД СЫРЬЯ И МАТЕРИАЛОВ": "ВК СКЛАД",
        "ИНСТРУМЕНТАЛЬНЫЙ УЧАСТОК": "ИУ",
        "ОТДЕЛ ГЛАВНОГО ТЕХНОЛОГА": "ОТГ",
        "ОТДЕЛ ИНФОРМАЦИОННЫХ ТЕХНОЛОГИЙ": "ОИТ",
        "ОТДЕЛ КОРПОРАТИВНОЙ БЕЗОПАСНОСТИ": "ОКБ",
        "ОТДЕЛ МАРКЕТИНГА": "ОМ",
        "ОТДЕЛ МАТЕРИАЛЬНО-ТЕХНИЧЕСКОГО СНАБЖЕНИЯ": "ОМТС",
        "ОТДЕЛ ПО ПЛАНИРОВАНИЮ ПРОИЗВОДСТВА": "ПЛАНИРОВАНИЮ ПРОИЗВОДСТВА",
        "ОТДЕЛ ПО ПРАВОВОЙ РАБОТЕ": "отдел по правовой работе",
        "ОТДЕЛ ПО РАБОТЕ С ПЕРСОНАЛОМ": "ОП",
        "ОТДЕЛ ПРОДАЖ": "ОТДЕЛ ПРОДАЖ",
        "ОТДЕЛ СИСТЕМ МЕНЕДЖМЕНТА И СЕРТИФИКАЦИИ": "ОТДЕЛ СИСТЕМ МЕНЕДЖМЕНТА И СЕРТИФИКАЦИИ",
        "ОТДЕЛ ТЕХНИЧЕСКОГО КОНТРОЛЯ": "ОТК",
        "ПЛАНОВО-ЭКОНОМИЧЕСКИЙ ОТДЕЛ": "ПЛАНОВО-ЭКОНОМИЧЕСКИЙ ОТДЕЛ",
        # "РУКОВОДСТВО И ОТДЕЛЬНЫЕ РАБОТНИКИ": "",
        "СБОРОЧНЫЙ УЧАСТОК (ВК)": "СУ",
        "СЕКТОР ПО РЕМОНТУ И ЭКСПЛУАТАЦИИ ЗДАНИЙ И СООРУЖЕНИЙ": "СЕКТОР ПО РЕМОНТУ И ЭКСПЛУАТАЦИИ ЗДАНИЙ И СООРУЖЕНИЙ",
        "СКЛАДСКОЕ ХОЗЯЙСТВО": "СКЛАД",
        "ТРАНСПОРТНЫЙ УЧАСТОК": "ТУ",
        "УЧАСТОК ПЕРЕРАБОТКИ ПЛАСТМАСС": "УПП",
        "УЧАСТОК ПРОИЗВОДСТВА СКПГ": "СКПГ",
        "ЦЕНТРАЛЬНЫЙ СКЛАД": "СКЛАД",
        "ЭНЕРГО-МЕХАНИЧЕСКИЙ ОТДЕЛ": "ЭМО",
    }
    return key if key not in departments else departments[key]
