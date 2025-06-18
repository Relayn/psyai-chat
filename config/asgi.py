"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application

# Импортируем маршруты нашего приложения chat
import chat.routing

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Получаем стандартное ASGI-приложение для обработки HTTP-запросов
django_asgi_app = get_asgi_application()

# ProtocolTypeRouter будет проверять тип входящего соединения
# и направлять его в соответствующий обработчик.
application = ProtocolTypeRouter(
    {
        # Для обычных HTTP-запросов используется стандартный обработчик Django.
        "http": django_asgi_app,
        # Для WebSocket-соединений мы используем наш собственный обработчик.
        "websocket": AuthMiddlewareStack(
            # AuthMiddlewareStack позволяет получить доступ к пользователю
            # (request.user) внутри нашего Consumer'а.
            URLRouter(
                # URLRouter направляет соединения к нужному консьюмеру
                # на основе URL-пути, используя шаблоны из chat.routing.
                chat.routing.websocket_urlpatterns
            )
        ),
    }
)