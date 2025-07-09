from django.conf import settings
from django.db import models


class Payment(models.Model):
    """
    Модель для отслеживания платежей через ЮKassa.

    Attributes:
        user (ForeignKey): Пользователь, совершивший платеж.
        yookassa_payment_id (CharField): Уникальный идентификатор платежа
            в системе ЮKassa.
        amount (DecimalField): Сумма платежа.
        status (CharField): Текущий статус платежа (PENDING, SUCCEEDED, CANCELED).
        created_at (DateTimeField): Время создания записи о платеже.
        updated_at (DateTimeField): Время последнего обновления статуса.
    """

    class Status(models.TextChoices):
        """Статусы платежа, соответствующие статусам ЮKassa."""

        PENDING = "PENDING", "Ожидает оплаты"
        SUCCEEDED = "SUCCEEDED", "Успешно оплачен"
        CANCELED = "CANCELED", "Отменен"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="payments",
        verbose_name="Пользователь",
    )
    yookassa_payment_id = models.CharField(
        max_length=255,
        unique=True,
        verbose_name="ID платежа в ЮKassa",
        help_text="Используется для идемпотентности вебхуков.",
    )
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Сумма")
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время обновления")

    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"
        ordering = ["-created_at"]

    def __str__(self):
        user_info = self.user.username if self.user else "N/A"
        return f"Платеж {self.id} от {user_info} на сумму {self.amount}"
