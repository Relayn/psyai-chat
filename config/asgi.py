"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.2/howto/deployment/asgi/
"""

import os

from django.core.asgi import get_asgi_application

# --- 1. Сначала конфигурируем Django ---
# Эта строка говорит Django, где найти файл настроек.
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
# Эта функция выполняет всю магию по настройке Django.
django_asgi_app = get_asgi_application()

# --- 2. И только ПОСЛЕ этого импортируем код наших приложений ---
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import chat.routing


# --- 3. Собираем итоговое приложение ---
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