from django.urls import path
from . import views

app_name = "post"

urlpatterns = [
    path('week/', views.posts, name="week"),
]
