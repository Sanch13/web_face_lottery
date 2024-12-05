from django.urls import path
from .views import get_all_tg_users

app_name = "webfacetg"

urlpatterns = [
    path('users/', get_all_tg_users, name="get_all_tg_users"),
]
