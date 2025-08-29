from django.conf import settings
from django.db import models

from users.models import User


class Payment(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Ожидает оплаты"
        SUCCEEDED = "SUCCEEDED", "Успешно оплачен"
        CANCELED = "CANCELED", "Отменен"

    id: int
    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="payments",
        verbose_name="Пользователь",
    )
    yookassa_payment_id: models.CharField = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="ID платежа в ЮKassa",
        help_text="Используется для идемпотентности вебхуков.",
    )
    amount: models.DecimalField = models.DecimalField(
        max_digits=10, decimal_places=2, verbose_name="Сумма"
    )
    status: models.CharField = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус",
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, verbose_name="Время создания"
    )
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True, verbose_name="Время обновления"
    )

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        user_info = self.user.username if isinstance(self.user, User) else "N/A"
        amount_str = f"{self.amount:.2f}"
        return f"Платеж {self.id} от {user_info} на сумму {amount_str}"
