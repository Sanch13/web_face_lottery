from django.urls import path, include
from rest_framework.routers import DefaultRouter
from post.api_views import TelegramPostViewSet

app_name = 'posts_api'

router = DefaultRouter()
router.register(r'posts', TelegramPostViewSet, basename='posts')

urlpatterns = [
    path('', include(router.urls)),
]
