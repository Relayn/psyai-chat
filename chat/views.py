from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404

from .models import ChatSession


@login_required
def chat_room(request):
    """
    Отображает страницу с чатом.
    Доступно только для аутентифицированных пользователей.
    """
    return render(request, "chat/chat_room.html")


@login_required
def chat_history_list(request):
    """
    Отображает список всех прошлых сессий чата для текущего пользователя.
    """
    sessions = ChatSession.objects.filter(user=request.user)
    return render(
        request, "chat/chat_history_list.html", {"sessions": sessions}
    )


@login_required
def chat_history_detail(request, session_id: int):
    """
    Отображает детальную историю сообщений для одной конкретной сессии.
    """
    session = get_object_or_404(ChatSession, id=session_id, user=request.user)
    return render(
        request, "chat/chat_history_detail.html", {"session": session}
    )