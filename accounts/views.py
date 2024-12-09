from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import UserLoginForm


def user_login(request):
    if request.method == "POST":
        user_login_form = UserLoginForm(request.POST)
        if user_login_form.is_valid():
            email = user_login_form.cleaned_data['email']
            password = user_login_form.cleaned_data['password']

            # Аутентификация по email и паролю
            user = authenticate(request, email=email, password=password)

            if user is not None and user.is_active and user.is_admin:
                login(request, user)
                messages.success(request, "Вы успешно вошли в систему.")
                return redirect('home')  # Замените 'home' на ваш URL
            else:
                messages.error(request, "Неправильный email или пароль.")
    else:
        user_login_form = UserLoginForm()

    return render(request, 'accounts/login.html', {'form': user_login_form})


def logout_view(request):
    logout(request)  # Завершаем сессию пользователя
    return redirect(to="accounts:login")  # Перенаправляем на страницу логина
