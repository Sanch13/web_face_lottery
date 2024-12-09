from django.contrib.auth import logout
from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

from .forms import EditTelegramUserForm
from .models import TelegramUser, Lottery, Ticket
from .utils import create_list_of_participants_lottery


def home(request):
    return redirect(to="accounts:login")
    # return render(request=request,
    #               template_name='webfacetg/home.html')


def get_list_lotteries(request):
    name_lotteries = {
        "lantern": "Розыгрыш умного проектора"
    }

    lotteries = Lottery.objects.using("psql").all()

    # Добавляем описания лотерей в список
    lotteries_with_names = [
        {
            'lottery': lottery,
            'display_name': name_lotteries.get(lottery.name, lottery.name)
        }
        for lottery in lotteries
    ]

    context = {
        'lotteries': lotteries_with_names
    }
    return render(request=request,
                  template_name="webfacetg/list_lotteries.html",
                  context=context)


def get_all_tg_users(request):
    users = TelegramUser.objects.using('psql').filter(is_active=True)
    context = {
        "users": users
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
    tickets = Ticket.objects.using("psql").filter(lottery=pk).select_related('user').order_by('ticket_number')
    # tickets = Ticket.objects.using("psql").prefetch_related('user').order_by('ticket_number')

    context = {
        "tickets": tickets,
        "lottery": pk
    }
    return render(request=request,
                  template_name="webfacetg/lottery_detail.html",
                  context=context)


class DeactivateUserAPIView(APIView):
    def patch(self, request, user_id):
        try:
            user = TelegramUser.objects.using('psql').get(pk=user_id)
            user.is_active = False
            user.save()
            return Response({"message": "Пользователь деактивирован."}, status=status.HTTP_200_OK)
        except TelegramUser.DoesNotExist:
            return Response({"error": "Пользователь не найден."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"error": f"Произошла ошибка: {str(e)}"},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


def download_participants_lottery(request, pk):
    tickets = Ticket.objects.using("psql").filter(lottery=pk).select_related('user').order_by('ticket_number')

    # Подготавливаем данные для DataFrame
    data = []
    for idx, ticket in enumerate(tickets, start=1):
        data.append({
            'Номер': idx,
            'ФИО Участника': ticket.user.full_name,
            'Билет': ticket.ticket_number
        })

    return create_list_of_participants_lottery(data)
