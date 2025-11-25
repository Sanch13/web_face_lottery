from django.shortcuts import render


def weekly_posts_editor(request):
    """Страница редактора постов на неделю"""
    return render(request, 'post/weekly_posts.html')
