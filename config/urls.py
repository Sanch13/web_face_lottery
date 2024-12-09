from django.contrib import admin
from django.shortcuts import render
from django.urls import path, include
from django.conf import settings
from django.conf.urls import handler404
from django.conf.urls.static import static

import accounts
from webfacetg.views import home, DeactivateUserAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('accounts/', include("accounts.urls", namespace='accounts')),
    path('telegram_users/', include("webfacetg.urls", namespace="tg_users")),
    path('api/users/<int:user_id>/deactivate/', DeactivateUserAPIView.as_view(),
         name='deactivate-user'),
]


# Кастомная функция для обработки 404
def custom_404(request, exception):
    return render(request, '404.html', status=404)


# Назначаем обработчик
handler404 = custom_404

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
