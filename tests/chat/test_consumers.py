import json
from datetime import timedelta

import pytest
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.utils import timezone

from chat.consumers import ChatConsumer
from chat.models import ChatSession

pytestmark = pytest.mark.asyncio
User = get_user_model()

@pytest.mark.django_db(transaction=True)
async def test_chat_consumer_limit_by_message_count():
    user = await User.objects.acreate_user(username="testuser", password="password")
    communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat/")
    communicator.scope["user"] = user
    connected, _ = await communicator.connect()
    assert connected

    session = await ChatSession.objects.aget(user=user)
    session.message_count = ChatConsumer.SESSION_MESSAGE_LIMIT
    await session.asave()

    await communicator.send_to(text_data=json.dumps({"message": "Это сообщение сверх лимита"}))

    # Проверяем, что получили сообщение о лимите
    response = await communicator.receive_from()
    assert json.loads(response)["type"] == "limit.reached"

    # Проверяем, что следующим событием было закрытие соединения
    close_event = await communicator.receive_output()
    assert close_event["type"] == "websocket.close"
    assert close_event["code"] == 4001

@pytest.mark.django_db(transaction=True)
async def test_chat_consumer_limit_by_time():
    user = await User.objects.acreate_user(username="testuser2", password="password")
    communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat/")
    communicator.scope["user"] = user
    connected, _ = await communicator.connect()
    assert connected

    session = await ChatSession.objects.aget(user=user)
    session.start_time = timezone.now() - timedelta(minutes=ChatConsumer.SESSION_DURATION_LIMIT_MINUTES + 1)
    await session.asave()

    await communicator.send_to(text_data=json.dumps({"message": "Сообщение в просроченной сессии"}))

    # Проверяем, что получили сообщение о лимите
    response = await communicator.receive_from()
    assert json.loads(response)["type"] == "limit.reached"

    # Проверяем, что следующим событием было закрытие соединения
    close_event = await communicator.receive_output()
    assert close_event["type"] == "websocket.close"
    assert close_event["code"] == 4001

@pytest.mark.django_db(transaction=True)
async def test_anonymous_user_rejected():
    from django.contrib.auth.models import AnonymousUser
    communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat/")
    communicator.scope["user"] = AnonymousUser()
    connected, _ = await communicator.connect()
    assert not connected
    assert not await ChatSession.objects.filter(user__isnull=True).aexists()