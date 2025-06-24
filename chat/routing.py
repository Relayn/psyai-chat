from django.urls import re_path

from . import consumers

# Этот список будет содержать все WebSocket URL-шаблоны для нашего приложения.
websocket_urlpatterns = [
    re_path(r"^ws/chat/$", consumers.ChatConsumer.as_asgi()),
]