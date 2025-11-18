import requests

from django.shortcuts import render
from django.http import JsonResponse
from django.conf import settings


def posts(request):
    bot_token = settings.TELEGRAM_API_TOKEN
    channel_id = settings.TELEGRAM_CHAT_ID

    # видео
    # url = f"https://api.telegram.org/bot{bot_token}/sendVideo"
    #
    # try:
    #     # URL видео файла
    #     video_url = "https://www.pexels.com/ru-ru/download/video/34699000/?fps=30.0&h=640&w=360"
    #     text = f"""\n🎉 Поздравляем с Днём рождения!🎂\n\n⭐ Джайчиеву Оксану Ивановну (ОТК) 💵\n⭐ Баркуна Антона Юрьевича (СУ) 💸\n#Сднемрождения 🥳\nПусть жизнь будет наполнена целями, смыслом, идеями, желаниями, которые унесут к вершинам успеха! 🚀 Любви и ощущения свободы в сердце! 💖"""
    #
    #     # Скачиваем видео
    #     video_response = requests.get(video_url, timeout=60)
    #     video_response.raise_for_status()
    #
    #     payload = {
    #         'chat_id': channel_id,
    #         'caption': text,
    #         'parse_mode': 'HTML',
    #         'supports_streaming': True  # Для возможности потокового воспроизведения
    #     }
    #
    #     files = {
    #         'video': ('birthday_video.mp4', video_response.content, 'video/mp4')
    #     }
    #
    #     response = requests.post(url, data=payload, files=files, timeout=60)
    #     response.raise_for_status()
    #
    #     return JsonResponse({
    #         'status': 'success',
    #         'message': "Видео успешно отправлено"
    #     })
    #
    # except Exception as e:
    #     return JsonResponse({
    #         'status': 'error',
    #         'message': f'Не удалось отправить видео: {str(e)}'
    #     }, status=400)

    # гифка
    # url = f"https://api.telegram.org/bot{bot_token}/sendAnimation"
    #
    # try:
    #     # Скачиваем изображение
    #     gif_url = "https://i.gifer.com/h6w.gif"
    #     text = f"""\n🎉 Поздравляем с Днём рождения!🎂\n\n⭐ Джайчиеву Оксану Ивановну (ОТК) 💵\n⭐ Баркуна Антона Юрьевича (СУ) 💸\n#Сднемрождения 🥳\nПусть жизнь будет наполнена целями, смыслом, идеями, желаниями, которые унесут к вершинам успеха! 🚀 Любви и ощущения свободы в сердце! 💖"""
    #     gif_response = requests.get(gif_url, timeout=60)
    #     gif_response.raise_for_status()
    #
    #     payload = {
    #         'chat_id': channel_id,
    #         'caption': text,
    #         'parse_mode': 'HTML'
    #     }
    #
    #     files = {
    #         'animation': ('birthday.gif', gif_response.content, 'image/gif')
    #     }
    #
    #     response = requests.post(url, data=payload, files=files, timeout=60)
    #     response.raise_for_status()
    #
    #     return JsonResponse({
    #         'status': 'success',
    #         'message': "Успешно отправлено"
    #     })
    #
    # except Exception as e:
    #     return JsonResponse({
    #         'status': 'error',
    #         'message': f'Не удалось отправить GIF: {str(e)}'
    #     }, status=400)

    # отправка фото
    url = f"https://api.telegram.org/bot{bot_token}/sendPhoto"

    try:
        # Скачиваем изображение
        image_url = "https://images.unsplash.com/photo-1762923634107-52d04a74c0cf?q=80&w=1481&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
        text = f"""\n🎉 Поздравляем с Днём рождения!🎂\n\n⭐ Джайчиеву Оксану Ивановну (ОТК) 💵\n⭐ Баркуна Антона Юрьевича (СУ) 💸\n#Сднемрождения 🥳\nПусть жизнь будет наполнена целями, смыслом, идеями, желаниями, которые унесут к вершинам успеха! 🚀 Любви и ощущения свободы в сердце! 💖"""
        image_response = requests.get(image_url, timeout=60)
        image_response.raise_for_status()

        payload = {
            'chat_id': channel_id,
            'caption': text,
            'parse_mode': 'HTML'
        }

        files = {
            'photo': ('daily_post.jpg', image_response.content, 'image/jpeg')
        }

        response = requests.post(url, data=payload, files=files, timeout=60)
        response.raise_for_status()

        return JsonResponse({
            'status': 'success',
            'message': "Успешно отправлено"
        })

    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': f'Не удалось отправить сообщение: {str(e)}'
        }, status=400)
