import json
from decimal import Decimal
from unittest.mock import MagicMock, patch

import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse

from payments.models import Payment

User = get_user_model()
pytestmark = pytest.mark.django_db


@pytest.fixture
def user(db):
    """Фикстура для создания обычного пользователя."""
    return User.objects.create_user(username="testuser", password="password")


@pytest.fixture
def payment(user):
    """Фикстура для создания платежа в статусе PENDING."""
    return Payment.objects.create(
        user=user,
        yookassa_payment_id="2d34b3f7-000f-5000-8000-1d58a7d370b1",
        amount=Decimal("999.00"),
        status=Payment.Status.PENDING,
    )


def test_create_payment_redirects_for_anonymous(client):
    """Тест: анонимный пользователь перенаправляется на страницу входа."""
    url = reverse("payments:create_payment")
    response = client.get(url)
    assert response.status_code == 302
    assert response.url.startswith(reverse("login"))


@patch("payments.views.create_yookassa_payment")
def test_create_payment_success(mock_create_payment, client, user):
    """Тест: авторизованный пользователь успешно создает платеж."""
    # 1. Настройка (Arrange)
    client.login(username="testuser", password="password")
    url = reverse("payments:create_payment")

    # Настраиваем мок-объект, который вернет наш сервис
    mock_response = MagicMock()
    mock_response.id = "2d34b3f7-000f-5000-8000-1d58a7d370b1"
    mock_response.status = "pending"
    mock_response.confirmation.confirmation_url = "https://yookassa.ru/checkout/..."
    mock_create_payment.return_value = mock_response

    # 2. Действие (Act)
    response = client.get(url)

    # 3. Проверка (Assert)
    # Проверяем, что наш сервис был вызван
    mock_create_payment.assert_called_once()
    # Проверяем, что в БД создался объект Payment
    assert Payment.objects.count() == 1
    db_payment = Payment.objects.first()
    assert db_payment.user == user
    assert db_payment.status == Payment.Status.PENDING
    assert db_payment.yookassa_payment_id == mock_response.id
    # Проверяем, что пользователь был перенаправлен на страницу оплаты
    assert response.status_code == 302
    assert response.url == mock_response.confirmation.confirmation_url


# --- Тесты для вебхука ---

def test_webhook_forbidden_for_invalid_ip(client, payment):
    """Тест: вебхук возвращает 403, если IP не из списка ЮKassa."""
    url = reverse("payments:yookassa_webhook")
    payload = {}  # Содержимое не важно для этого теста
    response = client.post(
        url,
        data=json.dumps(payload),
        content_type="application/json",
        REMOTE_ADDR="1.2.3.4",  # Недоверенный IP
    )
    assert response.status_code == 403


def test_webhook_success_updates_payment(client, payment, settings):
    """Тест: успешный вебхук обновляет статус платежа на SUCCEEDED."""
    url = reverse("payments:yookassa_webhook")
    payload = {
        "type": "notification",
        "event": "payment.succeeded",
        "object": {
            "id": payment.yookassa_payment_id,
            "status": "succeeded",
            "amount": {"value": "999.00", "currency": "RUB"},
            "paid": True,
        },
    }
    # Используем первый IP из разрешенного списка для теста
    allowed_ip = settings.YOOKASSA_WEBHOOK_IPS[0].split("/")[0]

    response = client.post(
        url,
        data=json.dumps(payload),
        content_type="application/json",
        REMOTE_ADDR=allowed_ip,
    )

    assert response.status_code == 200
    payment.refresh_from_db()
    assert payment.status == Payment.Status.SUCCEEDED


def test_webhook_idempotency(client, payment, settings):
    """Тест: повторный вебхук для уже успешного платежа не вызывает ошибок."""
    # Устанавливаем платежу статус "успешный"
    payment.status = Payment.Status.SUCCEEDED
    payment.save()

    url = reverse("payments:yookassa_webhook")
    payload = {
        "type": "notification",
        "event": "payment.succeeded",
        "object": {"id": payment.yookassa_payment_id, "status": "succeeded"},
    }
    allowed_ip = settings.YOOKASSA_WEBHOOK_IPS[0].split("/")[0]

    response = client.post(
        url,
        data=json.dumps(payload),
        content_type="application/json",
        REMOTE_ADDR=allowed_ip,
    )

    assert response.status_code == 200
    payment.refresh_from_db()
    assert payment.status == Payment.Status.SUCCEEDED