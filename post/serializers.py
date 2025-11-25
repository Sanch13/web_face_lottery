from rest_framework import serializers
from post.models import TelegramPost, MediaContent, TextTemplate


class MediaContentSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaContent
        fields = ['id', 'title', 'media_type', 'media_file']


class TextTemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = TextTemplate
        fields = ['id', 'title', 'text', 'is_active']


class TelegramPostSerializer(serializers.ModelSerializer):
    media_content = MediaContentSerializer(read_only=True)
    text_template = TextTemplateSerializer(read_only=True)

    # Поля для редактирования
    final_text = serializers.CharField(required=False, allow_blank=True)
    title = serializers.CharField(required=False)

    class Meta:
        model = TelegramPost
        fields = [
            'id', 'post_date', 'title', 'media_content', 'text_template',
            'final_text', 'people_count', 'status',
            'published_at', 'created_at'
        ]
        read_only_fields = [
            'id', 'post_date', 'media_content', 'text_template',
            'people_count', 'published_at',
            'created_at'
        ]