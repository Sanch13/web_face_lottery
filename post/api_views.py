from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.db import transaction
from post.models import TelegramPost
from post.serializers import TelegramPostSerializer


class TelegramPostViewSet(viewsets.ModelViewSet):
    queryset = TelegramPost.objects.all()
    serializer_class = TelegramPostSerializer

    def get_queryset(self):
        """Получить посты на 7 дней вперед от текущей даты"""
        today = timezone.localtime().date()
        end_date = today + timedelta(days=6)

        return TelegramPost.objects.filter(
            post_date__gte=today,
            post_date__lte=end_date
        ).order_by('post_date')

    @action(detail=False, methods=['get'])
    def weekly_posts(self, request):
        """Получить посты на 7 дней вперед"""
        today = timezone.localtime().date()
        posts = self.get_queryset()

        # Создаем структуру с датами, даже если постов нет
        weekly_data = {}
        for i in range(7):
            current_date = today + timedelta(days=i)
            weekly_data[current_date.isoformat()] = None

        # Заполняем существующими постами
        for post in posts:
            weekly_data[post.post_date.isoformat()] = TelegramPostSerializer(post).data

        return Response({
            'start_date': today.isoformat(),
            'end_date': (today + timedelta(days=6)).isoformat(),
            'posts': weekly_data
        })

    @action(detail=True, methods=['post'])
    def update_post(self, request, pk=None):
        """Обновить конкретный пост"""
        try:
            post = self.get_object()
            serializer = TelegramPostSerializer(post, data=request.data, partial=True)

            if serializer.is_valid():
                with transaction.atomic():
                    serializer.save()
                    return Response({
                        'status': 'success',
                        'message': 'Пост успешно обновлен',
                        'post': serializer.data
                    })
            else:
                return Response({
                    'status': 'error',
                    'message': 'Ошибка валидации',
                    'errors': serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({
                'status': 'error',
                'message': str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
