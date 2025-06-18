from django.contrib.auth.decorators import login_required
from django.shortcuts import render


@login_required
def chat_room(request):
    """
    Отображает страницу с чатом.
    Доступно только для аутентифицированных пользователей.
    """
    return render(request, "chat/chat_room.html")