from unittest.mock import AsyncMock, patch

import pytest
from django.contrib.auth import get_user_model

from chat.models import ChatMessage, ChatSession
from chat.tasks import process_gpt_request

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def user(db):
    """Фикстура для создания пользователя."""
    return User.objects.create_user(username="testuser", password="password")


@pytest.fixture
def chat_session(user):
    """Фикстура для создания сессии чата."""
    return ChatSession.objects.create(user=user)


@patch("chat.tasks.get_gpt_response")
@patch("chat.tasks.get_channel_layer")
def test_process_gpt_request_success(
    mock_get_channel_layer, mock_get_gpt_response, chat_session
):
    """
    Тестирует успешное выполнение задачи process_gpt_request.
    """
    # Arrange
    mock_get_gpt_response.return_value = "Это тестовый ответ от ИИ."
    mock_channel_layer = mock_get_channel_layer.return_value
    # Заменяем метод send на асинхронный мок, чтобы избежать UserWarning
    mock_channel_layer.send = AsyncMock()

    # Act
    process_gpt_request(chat_session.id, "Привет, ИИ!", "test_channel")

    # Assert
    # 1. Проверяем, что ответ от GPT был запрошен
    mock_get_gpt_response.assert_called_once()
    # 2. Проверяем, что сообщение от ИИ сохранилось в БД
    assert ChatMessage.objects.filter(
        session=chat_session, sender_type=ChatMessage.SenderType.AI
    ).exists()
    # 3. Проверяем, что сообщение было отправлено обратно клиенту
    mock_channel_layer.send.assert_called_once()


def test_process_gpt_request_session_not_found():
    """
    Тестирует случай, когда задача вызывается с несуществующим ID сессии.
    Задача должна обработать исключение и не "упасть".
    """
    # Act & Assert
    try:
        # Вызываем задачу с ID, которого точно нет в БД
        process_gpt_request(99999, "Любой промпт", "test_channel")
    except Exception as e:
        pytest.fail(f"Задача не должна выбрасывать исключение, но выбросила: {e}")


@patch("chat.tasks.get_gpt_response")
def test_process_gpt_request_generic_exception(mock_get_gpt_response, chat_session):
    """
    Тестирует случай, когда внутри задачи происходит непредвиденная ошибка.
    Задача должна обработать исключение и не "упасть".
    """
    # Arrange
    # Мокируем сервис так, чтобы он вызывал ошибку
    mock_get_gpt_response.side_effect = ValueError("Случилась непредвиденная ошибка")

    # Act & Assert
    try:
        process_gpt_request(chat_session.id, "Любой промпт", "test_channel")
    except Exception as e:
        pytest.fail(f"Задача не должна выбрасывать исключение, но выбросила: {e}")
