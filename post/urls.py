from django.urls import path
from . import views

app_name = "post"

urlpatterns = [
    path('weekly-posts/', views.weekly_posts_editor, name='weekly_posts_editor'),
]
