import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
def test_signup_view(client):
    """
    Тестирует страницу регистрации.
    1. Проверяет, что страница доступна по GET-запросу.
    2. Проверяет, что новый пользователь успешно создается через POST-запрос.
    """
    signup_url = reverse("signup")
    response = client.get(signup_url)
    assert response.status_code == 200, "Страница регистрации должна быть доступна."

    assert User.objects.count() == 0

    user_data = {
        "username": "testuser",
        "email": "test@example.com",
        "password1": "testpassword123",
        "password2": "testpassword123",
    }
    response = client.post(signup_url, data=user_data)

    assert response.status_code == 302, "После регистрации должен быть редирект."
    assert response.url == reverse("login"), "Редирект должен вести на страницу входа."

    assert User.objects.count() == 1
    assert User.objects.first().username == "testuser"


@pytest.mark.django_db
def test_login_and_profile_access(client):
    """
    Тестирует вход пользователя и доступ к странице профиля.
    1. Создает пользователя.
    2. Пытается войти.
    3. Проверяет доступ к странице профиля после входа.
    """
    user_password = "testpassword123"
    _ = User.objects.create_user(username="loginuser", password=user_password)

    profile_url = reverse("profile")
    response = client.get(profile_url)
    assert response.status_code == 302, (
        "Анонимный пользователь должен быть перенаправлен."
    )
    assert reverse("login") in response.url, "Редирект должен вести на страницу входа."

    login_url = reverse("login")
    response = client.post(
        login_url, {"username": "loginuser", "password": user_password}
    )

    assert response.status_code == 302
    assert response.url == reverse("profile")

    response = client.get(profile_url)
    assert response.status_code == 200
    assert "Добро пожаловать, loginuser!" in response.content.decode("utf-8")
