from django.shortcuts import render

from .models import TelegramUser


def get_all_tg_users(request):
    users = TelegramUser.objects.using('psql').all()
    context = {
        "users": users
    }
    return render(request=request,
                  template_name="webfacetg/users.html",
                  context=context)
