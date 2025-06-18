from django.urls import re_path

from . import consumers

# Этот список будет содержать все WebSocket URL-шаблоны для нашего приложения.
websocket_urlpatterns = [
    # re_path использует регулярные выражения для сопоставления URL.
    # r"^ws/chat/$" - это шаблон, который будет соответствовать URL "ws://<your_domain>/ws/chat/".
    # consumers.ChatConsumer.as_asgi() - это ASGI-приложение, которое будет обрабатывать соединение.
    re_path(r"^ws/chat/$", consumers.ChatConsumer.as_asgi()),
]