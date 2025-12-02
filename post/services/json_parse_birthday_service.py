import os
import json
import logging
from datetime import datetime

from django.db import transaction
from django.conf import settings

from post.models import BirthdayPerson

logger = logging.getLogger('celery_tasks')


class JsonImportService:
    def import_birthday_data(self, json_file_path=settings.PATH_TO_JSON_FILE):
        try:
            logger.info(f"Проверка файла: {json_file_path}")

            if not os.path.exists(json_file_path):
                logger.error(f"Файл не найден: {json_file_path}")
                return False

            try:
                with open(json_file_path, 'r', encoding='utf-8-sig') as file:
                    data = json.load(file)
            except json.JSONDecodeError as e:
                logger.error(f"Ошибка структуры JSON: {e}")
                return False
            except OSError as e:
                logger.error(f"Ошибка ОС при открытии файла: {e}")
                return False

            success_count = 0
            error_count = 0
            errors = []

            with transaction.atomic():
                for date_str, people_list in data.items():
                    try:
                        # Парсим дату из формата DD.MM.YYYY
                        date_obj = datetime.strptime(date_str, '%d.%m.%Y').date()

                        for person_data in people_list:
                            try:
                                success = self._import_person_record(person_data, date_obj)
                                if success:
                                    success_count += 1
                                else:
                                    error_count += 1
                            except Exception as e:
                                logger.exception(f"Ошибка {e}")

                                error_count += 1
                                fio = person_data.get('fio', 'Unknown')
                                errors.append(f"{date_str}: {fio} - {str(e)}")

                    except ValueError as e:
                        error_count += 1
                        errors.append(f"Неверный формат даты: {date_str}")
                    except Exception as e:
                        error_count += 1
                        errors.append(f"Ошибка обработки даты {date_str}: {str(e)}")

            if errors:
                logger.error("   Ошибки:")
                for error in errors[:10]:  # Показываем первые 10 ошибок
                    logger.error(f"     - {error}")
                if len(errors) > 10:
                    logger.error(f"     ... и ещё {len(errors) - 10} ошибок")

            return success_count, error_count, errors

        except Exception as e:
            logger.exception(f"Ошибка чтения файла: {e}")
            return False

    def _import_person_record(self, record, target_date):
        """Импорт одной записи человека"""
        # Валидация обязательных полей
        required_fields = ['fio', 'date_birthday']
        for field in required_fields:
            if field not in record:
                raise ValueError(f"Отсутствует обязательное поле: {field}")

        # Парсим дату рождения из формата DD.MM.YYYY
        try:
            date_birthday = datetime.strptime(record['date_birthday'], '%d.%m.%Y').date()
        except ValueError:
            raise ValueError(f"Неверный формат даты рождения: {record['date_birthday']}")

        # Ищем существующую запись
        existing_person = BirthdayPerson.objects.filter(
            fio=record['fio'],
            date_birthday=date_birthday
        ).first()

        if existing_person:
            # ОБНОВЛЯЕМ существующую запись
            existing_person.department = record.get('department', existing_person.department)
            existing_person.position = record.get('position', existing_person.position)
            existing_person.import_date = datetime.now().date()
            existing_person.save()

            logger.info(f"   🔄 Обновлен: {record['fio']} "
                        f"Отдел: {existing_person.department} "
                        f"Должность: {existing_person.position}")
            return True
        else:
            # СОЗДАЕМ новую запись
            BirthdayPerson.objects.create(
                fio=record['fio'],
                department=record.get('department', 'Не указан'),
                position=record.get('position', ''),
                date_birthday=date_birthday
            )
        logger.info(
            f"   ✅ Добавлен: {record['fio']} Birthday {target_date} {date_birthday} {record.get('department', '')} {record.get('position', '')}")
        return True

    def cleanup_file(self, json_file_path=settings.PATH_TO_JSON_FILE):
        """Удаляет JSON файл после обработки"""
        try:
            if os.path.exists(json_file_path):
                os.remove(json_file_path)
                logger.info(f"🗑️ Файл удален: {json_file_path}")
                return True
            return False
        except Exception as e:
            logger.exception(f"⚠️ Ошибка при удалении файла: {e}")
            return False
