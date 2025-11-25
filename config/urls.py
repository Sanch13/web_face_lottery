from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from django.conf import settings
from django.conf.urls import handler404
from django.conf.urls.static import static

from webfacetg.views import home, DeactivateUserAPIView
from webfacetg.api_views import LotteryUpdateView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/', include("accounts.urls", namespace='accounts')),
    path('telegram_users/', include("webfacetg.urls", namespace="tg_users")),
    path('posts/', include("post.urls", namespace="posts")),

    path('api/', include("post.api_urls", namespace="posts_api")),

    path('api/users/<int:user_id>/deactivate/', DeactivateUserAPIView.as_view(),
         name='deactivate-user'),
    path("api/v1/lotteries/<int:lottery_id>/", LotteryUpdateView.as_view(),
         name="get_lottery_by_id"),
]


# Кастомная функция для обработки 404
def custom_404(request, exception):
    return render(request, '404.html', status=404)


# Назначаем обработчик
handler404 = custom_404

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
