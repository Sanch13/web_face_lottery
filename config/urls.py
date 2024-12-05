from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('telegram_users/', include("webfacetg.urls", namespace="tg_users")),
]
