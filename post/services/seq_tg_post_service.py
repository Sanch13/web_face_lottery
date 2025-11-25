import logging

from post.models import MediaContent, TextTemplate, TelegramPost, BirthdayPerson
from post.utils import parse_emoji_and_format_people

logger = logging.getLogger('celery_tasks')


class SequentialPostService:
    def get_media_by_date(self, date):
        """Получить медиа для даты по принципу date_day % total_media"""
        active_media = MediaContent.objects.order_by('id')
        total_media = active_media.count()

        if total_media == 0:
            return None

        # Вычисляем индекс: день года % количество медиа
        day_of_year = date.timetuple().tm_yday
        media_index = (day_of_year - 1) % total_media  # -1 чтобы начать с 0

        return active_media[media_index]

    def get_text_by_date(self, date):
        """Получить текст для даты по принципу date_day % total_texts"""
        active_texts = TextTemplate.objects.filter(is_active=True).order_by('id')
        total_texts = active_texts.count()

        if total_texts == 0:
            return None

        day_of_year = date.timetuple().tm_yday
        text_index = (day_of_year - 1) % total_texts

        return active_texts[text_index]

    def get_birthday_people_for_date(self, target_date):
        """
        Получить именинников на указанную дату из таблицы BirthdayPerson
        """
        birthday_people = BirthdayPerson.objects.filter(
            date_birthday__month=target_date.month,
            date_birthday__day=target_date.day
        ).order_by('fio')

        if not birthday_people.exists():
            return None

        # Форматируем данные для шаблона
        people_data = []
        for person in birthday_people:
            people_data.append({
                'fio': person.fio,
                'department': person.department,
                'position': person.position
            })

        return people_data

    def generate_post_for_date(self, target_date):
        """Старый метод (для обратной совместимости)"""
        return self.generate_or_update_post_for_date(target_date)

    def generate_or_update_post_for_date(self, target_date):
        """
        Создать или ОБНОВИТЬ пост на указанную дату
        Если пост уже существует - обновляет список именинников
        """
        try:
            # Получаем именинников на эту дату
            birthday_people = self.get_birthday_people_for_date(target_date)
            current_people_count = len(birthday_people) if birthday_people else 0

            # Если нет именинников - удаляем пост если он есть
            if not birthday_people:
                deleted_count, _ = TelegramPost.objects.filter(
                    post_date=target_date,
                    status='scheduled'
                ).delete()
                if deleted_count > 0:
                    logger.info(f"🗑️ Удален пост на {target_date} - нет именинников")
                return None

            # Получаем медиа и текст
            media = self.get_media_by_date(target_date)
            text_template = self.get_text_by_date(target_date)

            if not media or not text_template:
                logger.info("Не найдены медиа или тексты для создания поста")
                return None

            # Форматируем текст с именинниками
            final_text = parse_emoji_and_format_people(text_template.text, birthday_people)

            # Проверяем, существует ли уже пост
            existing_post = TelegramPost.objects.filter(post_date=target_date).first()

            if existing_post:
                # Проверяем, изменилось ли количество именинников
                if existing_post.people_count == current_people_count:
                    logger.info(
                        f"⏭️ Пост на {target_date} не требует обновления. Именинников: {current_people_count}")
                    return "Пост актуален (без изменений)"

                # ОБНОВЛЯЕМ существующий пост
                existing_post.media_content = media
                existing_post.text_template = text_template
                existing_post.final_text = final_text
                existing_post.people_count = current_people_count
                existing_post.title = f"Пост {target_date} (обновлен)"
                existing_post.save()

                logger.info(
                    f"🔄 Обновлен пост на {target_date}. Именинников: {len(birthday_people)}")
                return "Пост обновлен"
            else:
                # СОЗДАЕМ новый пост
                TelegramPost.objects.create(
                    post_date=target_date,
                    title=f"Пост {target_date}",
                    media_content=media,
                    text_template=text_template,
                    final_text=final_text,
                    people_count=current_people_count,
                    status='scheduled'
                )

                logger.info(f"✅ Создан пост на {target_date}. Именинников: {len(birthday_people)}")
                return "Пост создан"

        except Exception as e:
            logger.error(f"❌ Ошибка при обработке поста на {target_date}: {str(e)}")
            return None
