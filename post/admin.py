from django.contrib import admin

from django.contrib import admin
from django.utils.html import format_html
from .models import MediaContent, TextTemplate, TelegramPost, BirthdayPerson


@admin.register(MediaContent)
class MediaContentAdmin(admin.ModelAdmin):
    # Убедитесь, что здесь список, а не метод
    list_display = ['id', 'title', 'media_type_badge', 'media_preview', 'file_size', 'created_at',
                    'action_buttons']
    list_filter = ['media_type', 'created_at']
    search_fields = ['title']
    readonly_fields = ['media_preview_large', 'file_size', 'created_at']
    list_per_page = 20

    # Если нужны кастомные действия - добавляем их здесь
    # actions = ['some_custom_action']

    fieldsets = [
        ('Основная информация', {
            'fields': ['title', 'media_type', 'media_file'],
            'classes': ['wide']
        }),
        ('Предпросмотр', {
            'fields': ['media_preview_large'],
            'classes': ['wide', 'collapse']
        }),
        ('Дополнительно', {
            'fields': ['file_size', 'created_at'],
            'classes': ['collapse']
        }),
    ]

    def media_type_badge(self, obj):
        """Бейдж типа медиа"""
        colors = {
            'photo': '#4CAF50',
            'animation': '#FF9800',
            'video': '#2196F3'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            colors.get(obj.media_type, '#666'),
            obj.get_media_type_display()
        )

    media_type_badge.short_description = 'Тип'

    def media_preview(self, obj):
        """Миниатюра в списке"""
        if obj.media_file:
            if obj.media_type in ['photo', 'animation']:
                return format_html(
                    '<img src="{}" style="max-height: 40px; max-width: 40px; border-radius: 4px;" title="{}" />',
                    obj.media_file.url, obj.title
                )
            elif obj.media_type == 'video':
                return format_html(
                    '<div style="width: 40px; height: 40px; background: #2196F3; color: white; '
                    'display: flex; align-items: center; justify-content: center; border-radius: 4px;" title="{}">'
                    '🎥</div>',
                    obj.title
                )
        return format_html('<span style="color: #ccc;">—</span>')

    media_preview.short_description = ''

    def media_preview_large(self, obj):
        """Большой предпросмотр"""
        if not obj.media_file:
            return format_html('<span style="color: #999;">Файл не загружен</span>')

        if obj.media_type == 'photo':
            return format_html(
                '<div style="text-align: center;">'
                '<img src="{}" style="max-height: 400px; max-width: 100%; border-radius: 8px;" />'
                '<br><small style="color: #666;">{}</small>'
                '</div>',
                obj.media_file.url, obj.media_file.name
            )
        elif obj.media_type == 'animation':
            return format_html(
                '<div style="text-align: center;">'
                '<img src="{}" style="max-height: 400px; max-width: 100%; border-radius: 8px;" />'
                '<br><small style="color: #666;">GIF: {}</small>'
                '</div>',
                obj.media_file.url, obj.media_file.name
            )
        elif obj.media_type == 'video':
            return format_html(
                '<div style="text-align: center;">'
                '<strong>🎥 Видео файл</strong><br>'
                '<small style="color: #666;">{}</small><br>'
                '<video controls style="max-height: 400px; max-width: 100%; border-radius: 8px;">'
                '<source src="{}" type="video/mp4">'
                'Ваш браузер не поддерживает видео.'
                '</video>'
                '</div>',
                obj.media_file.name, obj.media_file.url
            )

    media_preview_large.short_description = 'Предпросмотр файла'

    def file_size(self, obj):
        """Размер файла"""
        if obj.media_file:
            try:
                size = obj.media_file.size
                if size < 1024 * 1024:  # Меньше 1MB
                    return f"{size / 1024:.1f} KB"
                else:
                    return f"{size / (1024 * 1024):.1f} MB"
            except (OSError, ValueError):
                return "—"
        return "—"

    file_size.short_description = 'Размер'

    def action_buttons(self, obj):
        """Кнопки действий - переименовали метод"""
        return format_html(
            '<div style="white-space: nowrap;">'
            '<a href="{}" class="button" style="padding: 5px 10px; background: #417690; color: white; text-decoration: none; border-radius: 3px; font-size: 12px;">👁️ Просмотр</a>&nbsp;'
            '<a href="{}" class="button" style="padding: 5px 10px; background: #ba2121; color: white; text-decoration: none; border-radius: 3px; font-size: 12px;">🗑️ Удалить</a>'
            '</div>',
            f'{obj.id}/',
            f'{obj.id}/delete/'
        )

    action_buttons.short_description = 'Действия'


# Для TextTemplate
@admin.register(TextTemplate)
class TextTemplateAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', 'is_active', 'text_preview', 'created_at']
    list_filter = ['is_active', 'created_at']
    list_editable = ['is_active']
    search_fields = ['title', 'text']

    def text_preview(self, obj):
        return obj.text[:100] + "..." if len(obj.text) > 100 else obj.text

    text_preview.short_description = 'Текст (превью)'


# Для TelegramPost
@admin.register(TelegramPost)
class TelegramPostAdmin(admin.ModelAdmin):
    list_display = ['id', 'title', "post_date", 'status_badge', 'created_at']
    list_filter = ['status', 'post_date']
    readonly_fields = ['created_at', 'published_at']

    def status_badge(self, obj):
        colors = {
            'scheduled': '#FFA000',
            'published': '#4CAF50',
            'failed': '#F44336'
        }
        return format_html(
            '<span style="background-color: {}; color: white; padding: 3px 8px; border-radius: 12px; font-size: 11px;">{}</span>',
            colors.get(obj.status, '#666'),
            obj.get_status_display()
        )

    status_badge.short_description = 'Статус'


@admin.register(BirthdayPerson)
class BirthdayPersonAdmin(admin.ModelAdmin):
    list_display = ['fio', 'department', 'position', 'date_birthday', 'age_display']
    list_filter = ['department', 'import_date', 'date_birthday']
    search_fields = ['fio', 'department', 'position']
    readonly_fields = ['import_date', 'created_at']

    def age_display(self, obj):
        return obj.get_age()

    age_display.short_description = 'Возраст'

    def get_queryset(self, request):
        return super().get_queryset(request).order_by('date_birthday', 'fio')
