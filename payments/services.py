import uuid
from decimal import Decimal

from django.conf import settings
from yookassa import Configuration
from yookassa import Payment as YooPayment


def configure_yookassa_api():
    """Настраивает API ЮKassa с учетными данными из настроек."""

    Configuration.configure(settings.YOOKASSA_SHOP_ID, settings.YOOKASSA_SECRET_KEY)


def create_yookassa_payment(
    amount: Decimal, description: str, return_url: str
) -> YooPayment:
    """
    Создает платеж в системе ЮKassa.

    Args:
        amount: Сумма платежа.
        description: Описание платежа для пользователя.
        return_url: URL, на который пользователь вернется после оплаты.

    Returns:
        Объект платежа от API ЮKassa.
    """
    configure_yookassa_api()
    idempotence_key = str(uuid.uuid4())

    payment = YooPayment.create(
        {
            "amount": {"value": str(amount), "currency": "RUB"},
            "confirmation": {"type": "redirect", "return_url": return_url},
            "capture": True,
            "description": description,
            "metadata": {},
        },
        idempotence_key,
    )

    return payment
