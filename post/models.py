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
    status = models.CharField('Статус', max_length=20, choices=POST_STATUS, default='scheduled')
    published_at = models.DateTimeField('Время публикации', null=True, blank=True)
    created_at = models.DateTimeField('Дата создания', auto_now_add=True)

    def __str__(self):
        return f"Пост на {self.post_date}"

    class Meta:
        verbose_name = 'Telegram пост'
        verbose_name_plural = 'Telegram посты'
        ordering = ['post_date']
