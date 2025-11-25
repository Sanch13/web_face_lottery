from django.db import models
from django.contrib.auth.models import User


class MediaContent(models.Model):
    MEDIA_TYPES = [
        ('photo', 'Фото'),
        ('animation', 'GIF'),
        ('video', 'Видео'),
    ]

    title = models.CharField('Название', max_length=255)
    media_type = models.CharField('Тип медиа', max_length=20, choices=MEDIA_TYPES)
    media_file = models.FileField('Файл', upload_to='media_content/')
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return f"{self.title} ({self.get_media_type_display()})"

    class Meta:
        verbose_name = 'Медиа контент'
        verbose_name_plural = 'Медиа контент'


class TextTemplate(models.Model):
    title = models.CharField('Название', max_length=255)
    text = models.TextField('Текст шаблона')
    is_active = models.BooleanField('Активный', default=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = 'Шаблон текста'
        verbose_name_plural = 'Шаблоны текстов'


class TelegramPost(models.Model):
    POST_STATUS = [
        ('scheduled', 'Запланирован'),
        ('published', 'Опубликован'),
        ('failed', 'Ошибка'),
    ]

    post_date = models.DateField('Дата публикации', unique=True)
    title = models.CharField('Название поста', max_length=255)
    media_content = models.ForeignKey(MediaContent, on_delete=models.CASCADE, verbose_name='Медиа')
    text_template = models.ForeignKey(TextTemplate, on_delete=models.CASCADE, verbose_name='Текст')
    final_text = models.TextField('Финальный текст', blank=True)
    people_count = models.IntegerField('Количество именинников', default=0)
    status = models.CharField('Статус', max_length=20, choices=POST_STATUS, default='scheduled')
    published_at = models.DateTimeField('Время публикации', null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return f"Пост на {self.post_date}"

    class Meta:
        verbose_name = 'Telegram пост'
        verbose_name_plural = 'Telegram посты'
        ordering = ['post_date']


class BirthdayPerson(models.Model):
    fio = models.CharField('ФИО', max_length=255)
    department = models.CharField('Отдел', max_length=255)
    position = models.CharField('Должность', max_length=255, blank=True)
    date_birthday = models.DateField('Дата рождения')
    import_date = models.DateField('Дата импорта', auto_now_add=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    class Meta:
        verbose_name = 'Именинник'
        verbose_name_plural = 'Именинники'
        indexes = [
            models.Index(fields=['date_birthday']),
            models.Index(fields=['import_date']),
        ]

    def __str__(self):
        return f"{self.fio} ({self.department})"

    def get_age(self):
        """Вычисляет возраст на момент дня рождения в этом году"""
        from datetime import date
        today = date.today()
        age = today.year - self.date_birthday.year

        # Проверяем, был ли уже день рождения в этом году
        birthday_this_year = self.date_birthday.replace(year=today.year)
        if today < birthday_this_year:
            age -= 1

        return age

    def get_birthday_this_year(self):
        """Возвращает дату дня рождения в текущем году"""
        from datetime import date
        today = date.today()
        return self.date_birthday.replace(year=today.year)
