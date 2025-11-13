import json

from django.contrib.auth import logout
import redis

from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.conf import settings
from django.core.exceptions import ValidationError

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import IsAuthenticated

from .forms import EditTelegramUserForm, CreateLotteryForm
from .models import TelegramUser, Lottery, Ticket
from .utils import create_list_of_participants_lottery, create_list_all_users
from .services import add_lottery

redis_client = redis.StrictRedis(
    host=settings.REDIS_HOST,
    port=settings.REDIS_PORT,
    db=settings.REDIS_DB
)


def home(request):
    return redirect(to="accounts:login")
    # return render(request=request,
    #               template_name='webfacetg/home.html')


def get_list_lotteries(request):
    lotteries = Lottery.objects.using("psql").all()
    context = {
        'lotteries': lotteries
    }
    return render(request=request,
                  template_name="webfacetg/list_lotteries.html",
                  context=context)


def get_all_tg_users(request):
    users = TelegramUser.objects.using('psql').filter(is_active=True).order_by("full_name")
    list_edit_users = []
    for user in users:
        if len(user.full_name.split()) != 3:
            list_edit_users.append(user)
            continue
        if not user.full_name.istitle():
            list_edit_users.append(user)

    context = {
        "users": users,
        "edit_full_name": list_edit_users if list_edit_users else ''
    }
    return render(request=request,
                  template_name="webfacetg/users.html",
                  context=context)


@login_required
def edit_tg_user(request, pk):
    user = TelegramUser.objects.using('psql').get(pk=pk)

    if request.method == "POST":
        form = EditTelegramUserForm(data=request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Данные пользователя успешно обновлены!")
    else:
        form = EditTelegramUserForm(instance=user)

    context = {
        "form": form
    }
    return render(request=request,
                  template_name="webfacetg/edit_tg_user.html",
                  context=context)


def get_list_participants_lottery(request, pk):
    tickets = Ticket.objects.using("psql").filter(lottery=pk).select_related('user').filter(
        user__is_active=True).order_by('user__full_name')
    all_users = TelegramUser.objects.using("psql").filter(is_active=True)

    all_users_ids = [user.id for user in all_users]
    ticket_users = [ticket.user.id for ticket in tickets]
    diff_users = list(set(all_users_ids) - set(ticket_users))
    users_doesnt_tickets = all_users.filter(id__in=diff_users)

    is_active_lottery = Lottery.objects.using("psql").filter(pk=pk).values_list('is_active',
                                                                                flat=True).first()
    context = {
        "tickets": tickets,
        "lottery": pk,
        "is_active_lottery": is_active_lottery,
        "users_doesnt_tickets": users_doesnt_tickets
    }
    return render(request=request,
                  template_name="webfacetg/lottery_detail.html",
                  context=context)


class DeactivateUserAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, user_id):
        try:
            user = TelegramUser.objects.using('psql').get(pk=user_id)
            user.is_active = False
            user.save()
            data = {
                "full_name": user.full_name,
                "telegram_id": user.telegram_id,
            }
            redis_client.rpush('telegram_deactivate_user_queue', json.dumps(data))
            # redis_client.rpush('telegram_deactivate_user_queue', user.telegram_id)

            return Response({"message": "Пользователь деактивирован."}, status=status.HTTP_200_OK)
        except TelegramUser.DoesNotExist:
            return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Произошла ошибка: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def download_participants_lottery(request, pk):
    tickets = Ticket.objects.using("psql").filter(lottery=pk).select_related('user').order_by(
        'ticket_number')

    # Подготавливаем данные для DataFrame
    data = []
    for idx, ticket in enumerate(tickets, start=1):
        data.append({
            'Номер': idx,
            'ФИО Участника': ticket.user.full_name,
            'Билет': ticket.ticket_number
        })

    return create_list_of_participants_lottery(data)


def download_all_tg_users(request):
    users = TelegramUser.objects.using("psql").filter(is_active=True)

    # Подготавливаем данные для DataFrame
    data = []
    for idx, user in enumerate(users, start=1):
        data.append({
            'Номер': idx,
            'ФИО': user.full_name,
        })

    return create_list_all_users(data)


@login_required
def create_lottery(request):
    if request.method == 'POST':
        form = CreateLotteryForm(data=request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            name = cd["name"]
            description = cd["description"]
            is_active = cd["is_active"]
            if Lottery.objects.using("psql").filter(name=name).exists():
                form.add_error("name", "Такая лотерея уже существует")
            else:
                add_lottery(name, description, is_active)
                return redirect('webfacetg:create_lottery')
    else:
        form = CreateLotteryForm()

    lotteries = Lottery.objects.using("psql").all().order_by("-is_active", "-create")
    context = {
        "form": form,
        "lotteries": lotteries if lotteries else "",
    }
    return render(
        request=request,
        template_name="webfacetg/create_lottery.html",
        context=context
    )

# TODO: Why? Delete maybe?
# @login_required
# def create_user(request):
#     if request.method == "POST":
#         form = CreateUserForm(data=request.POST)
#         if form.is_valid():
#             cd = form.cleaned_data
#             telegram_id = cd["telegram_id"]
#             full_name = cd["full_name"]
#             full_name_from_tg = cd["full_name_from_tg"]
#             username = cd["username"]
#
#             add_user(telegram_id, full_name, full_name_from_tg, username)
#
#             return redirect("webfacetg:create_user")
#     else:
#         form = CreateUserForm()
#     context = {
#         "form": form
#     }
#     return render(
#         request=request,
#         template_name="webfacetg/tg_user_create.html",
#         context=context,
#     )
