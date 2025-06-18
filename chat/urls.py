from django.urls import path

from . import views

urlpatterns = [
    # URL для нашей комнаты чата.
    path("chat/", views.chat_room, name="chat_room"),
]