import json
from unittest.mock import patch

import pytest
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model

from chat.consumers import ChatConsumer
from chat.models import ChatMessage

pytestmark = pytest.mark.django_db(transaction=True)
User = get_user_model()


@pytest.mark.asyncio
@patch("chat.consumers.process_gpt_request.delay")
async def test_receive_triggers_celery_task(mock_process_gpt_request_delay):
    """
    Тестирует, что при получении сообщения от пользователя:
    1. Сообщение сохраняется в БД.
    2. Клиенту отправляется статус "ai.typing".
    3. Вызывается Celery-задача `process_gpt_request` с правильными аргументами.
    """
    # 1. Настройка (Arrange)
    user = await User.objects.acreate_user(username="async_user", password="password")
    test_channel_name = "test_specific_channel_name_for_this_test"
    communicator = WebsocketCommunicator(ChatConsumer.as_asgi(), "/ws/chat/")
    communicator.scope["channel_name"] = test_channel_name
    communicator.scope["user"] = user

    connected, _ = await communicator.connect()
    assert connected, "Соединение должно быть установлено"

    # 2. Действие (Act)
    test_message = "Привет, это тестовое сообщение"
    await communicator.send_to(text_data=json.dumps({"message": test_message}))

    # 3. Проверка (Assert)

    # 3.1. Проверяем, что consumer отправил статус "ИИ печатает..."
    response = await communicator.receive_from()
    response_data = json.loads(response)
    assert response_data["type"] == "ai.typing"
    assert response_data["payload"]["is_typing"] is True

    # 3.2. Проверяем, что сообщение пользователя сохранилось в БД
    assert await ChatMessage.objects.filter(
        text=test_message, sender_type=ChatMessage.SenderType.USER
    ).aexists()

    # 3.3. Проверяем, что наша Celery-задача была вызвана один раз
    mock_process_gpt_request_delay.assert_called_once()

    # 3.4. Проверяем, что задача была вызвана с корректными аргументами
    call_args = mock_process_gpt_request_delay.call_args
    assert "session_id" in call_args.kwargs
    assert call_args.kwargs["user_prompt"] == test_message
    # Проверяем, что используется channel_name, который мы передали в scope
    assert call_args.kwargs["channel_name"] == test_channel_name

    # Закрываем соединение
    await communicator.disconnect()
