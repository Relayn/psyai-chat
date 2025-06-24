import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

User = get_user_model()


@pytest.mark.django_db
def test_full_user_journey(client):
    """
    Тестирует полный пользовательский сценарий:
    1. Открывает страницу регистрации.
    2. Создает нового пользователя.
    3. Логинится под новым пользователем.
    4. Переходит в личный кабинет.
    5. Из личного кабинета переходит в чат.
    """
    # --- 1. Определение переменных ---
    signup_url = reverse("signup")
    login_url = reverse("login")
    profile_url = reverse("profile")
    chat_url = reverse("chat_room")
    user_data = {
        "username": "journey_user",
        "email": "journey@example.com",
        "password": "strongpassword123",
    }

    # --- 2. Регистрация ---
    # Убеждаемся, что пользователей пока нет
    assert User.objects.count() == 0

    # Отправляем POST-запрос для создания пользователя
    response = client.post(
        signup_url,
        {
            "username": user_data["username"],
            "email": user_data["email"],
            "password1": user_data["password"],
            "password2": user_data["password"],
        },
    )

    # Проверяем, что после регистрации нас перенаправило на страницу входа
    assert response.status_code == 302, "После регистрации должен быть редирект"
    assert response.url == login_url, "Редирект должен вести на страницу входа"
    assert User.objects.count() == 1, "Должен быть создан один пользователь"
    print("✅ Этап регистрации пройден успешно.")

    # --- 3. Вход в систему ---
    response = client.post(
        login_url,
        {"username": user_data["username"], "password": user_data["password"]},
    )

    # Проверяем, что после входа нас перенаправило в личный кабинет
    assert response.status_code == 302, "После входа должен быть редирект"
    assert response.url == profile_url, "Редирект должен вести в личный кабинет"
    print("✅ Этап входа в систему пройден успешно.")

    # --- 4. Доступ к личному кабинету ---
    response = client.get(profile_url)

    assert response.status_code == 200, "Личный кабинет должен быть доступен"
    # Проверяем, что на странице есть имя пользователя и ссылка на чат
    content = response.content.decode("utf-8")
    assert user_data["username"] in content, "В профиле должно быть имя пользователя"
    assert f'href="{chat_url}"' in content, "В профиле должна быть ссылка на чат"
    print("✅ Этап доступа к личному кабинету пройден успешно.")

    # --- 5. Переход в чат ---
    response = client.get(chat_url)

    assert response.status_code == 200, "Страница чата должна быть доступна"
    assert (
        "Чат с ИИ-психологом" in response.content.decode("utf-8")
    ), "На странице чата должен быть заголовок"
    print("✅ Этап перехода в чат пройден успешно. Интеграционный тест завершен!")