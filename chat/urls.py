from django.urls import path

from . import views

urlpatterns = [
    # URL для нашей комнаты чата.
    path("chat/", views.chat_room, name="chat_room"),
    # URL для списка сессий
    path("chat/history/", views.chat_history_list, name="chat_history_list"),
    # URL для детального просмотра сессии
    path(
        "chat/history/<int:session_id>/",
        views.chat_history_detail,
        name="chat_history_detail",
    ),
]