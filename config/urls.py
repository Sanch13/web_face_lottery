from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from webfacetg.views import home, DeactivateUserAPIView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', home, name='home'),
    path('telegram_users/', include("webfacetg.urls", namespace="tg_users")),
    path('api/users/<int:user_id>/deactivate/', DeactivateUserAPIView.as_view(), name='deactivate-user'),
    path('accounts/', include('accounts.urls', namespace='accounts')),
]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
