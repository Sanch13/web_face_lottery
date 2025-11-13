from django.urls import path
from . import views

app_name = "webfacetg"

urlpatterns = [
    path('users/', views.get_all_tg_users, name="get_all_tg_users"),
    path('users/edit/<int:pk>/', views.edit_tg_user, name="edit_users"),
    path('all_lotteries/', views.get_list_lotteries, name="all_lotteries"),
    path('create_lottery/', views.create_lottery, name="create_lottery"),
    path('users/lottery/<int:pk>/participants/',
         views.get_list_participants_lottery,
         name="lottery_users"),
    path('users/lottery/<int:pk>/participants/download/',
         views.download_participants_lottery,
         name='download_participants_lottery'),
    path('users/lottery/all_users/download/',
         views.download_all_tg_users,
         name='download_all_tg_users'),
]
