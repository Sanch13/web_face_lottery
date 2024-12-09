from django.contrib import messages
from django.shortcuts import render, redirect
from django.contrib.auth import login, authenticate


def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Аутентификация пользователя через AD
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('home')  # Перенаправление на главную страницу
        else:
            messages.error(request, "Неверные учётные данные")

    return render(request, 'accounts/login.html')
