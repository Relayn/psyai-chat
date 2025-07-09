import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from chat.models import ChatMessage, ChatSession

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def user_one(db):
    """Фикстура для создания первого пользователя."""
    return User.objects.create_user(username="user_one", password="password123")


@pytest.fixture
def user_two(db):
    """Фикстура для создания второго пользователя."""
    return User.objects.create_user(username="user_two", password="password123")


@pytest.fixture
def session_for_user_one(user_one):
    """Фикстура для создания сессии, принадлежащей user_one."""
    session = ChatSession.objects.create(user=user_one, message_count=2)
    ChatMessage.objects.create(
        session=session, text="Сообщение от user_one", sender_type="USER"
    )
    return session


@pytest.fixture
def session_for_user_two(user_two):
    """Фикстура для создания сессии, принадлежащей user_two."""
    return ChatSession.objects.create(user=user_two, message_count=1)


# --- Тесты для списка истории чатов ---


def test_chat_history_list_anonymous_redirect(client):
    """Тест: анонимный пользователь перенаправляется на страницу входа."""
    url = reverse("chat_history_list")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


def test_chat_history_list_shows_only_own_sessions(
    client, user_one, session_for_user_one, session_for_user_two
):
    """Тест: пользователь видит только свои сессии в списке."""
    client.login(username="user_one", password="password123")
    url = reverse("chat_history_list")
    response = client.get(url)

    assert response.status_code == 200
    # Проверяем, что сессия user_one присутствует на странице
    assert session_for_user_one.id in [s.id for s in response.context["sessions"]]
    # Проверяем, что сессия user_two ОТСУТСТВУЕТ на странице
    assert session_for_user_two.id not in [s.id for s in response.context["sessions"]]
    # Проверяем, что в контенте есть упоминание количества сообщений нашей сессии
    assert (
        f"Сообщений: {session_for_user_one.message_count}" in response.content.decode()
    )


# --- Тесты для детального просмотра истории ---


def test_chat_history_detail_anonymous_redirect(client, session_for_user_one):
    """Тест: анонимный пользователь перенаправляется при доступе к деталям."""
    url = reverse("chat_history_detail", args=[session_for_user_one.id])
    response = client.get(url)
    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


def test_chat_history_detail_owner_access(client, user_one, session_for_user_one):
    """Тест: владелец сессии может просматривать ее содержимое."""
    client.login(username="user_one", password="password123")
    url = reverse("chat_history_detail", args=[session_for_user_one.id])
    response = client.get(url)

    assert response.status_code == 200
    # Проверяем, что на странице есть текст сообщения из этой сессии
    assert "Сообщение от user_one" in response.content.decode()


def test_chat_history_detail_other_user_forbidden(
    client, user_two, session_for_user_one
):
    """
    Тест (Безопасность): пользователь не может просматривать чужую сессию.
    Ожидаем получить ошибку 404.
    """
    client.login(username="user_two", password="password123")
    # user_two пытается получить доступ к сессии, принадлежащей user_one
    url = reverse("chat_history_detail", args=[session_for_user_one.id])
    response = client.get(url)

    # get_object_or_404 должен вернуть статус 404
    assert response.status_code == 404
