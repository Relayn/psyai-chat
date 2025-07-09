from django.conf import settings
from django.db import models


class ImageAnalysisResult(models.Model):
    """
    Хранит результат анализа изображения, выполненного через внешний сервис.

    Модель отслеживает жизненный цикл асинхронной задачи анализа: от
    создания (`PENDING`) до завершения (`COMPLETED` или `FAILED`).

    Attributes:
        user (ForeignKey): Пользователь, запросивший анализ.
        source_image (ImageField): Исходное изображение, загруженное пользователем.
        status (CharField): Текущий статус задачи анализа.
        result_payload (JSONField): Полный JSON-ответ от внешнего API.
        error_message (TextField): Сообщение об ошибке, если анализ не удался.
        created_at (DateTimeField): Время создания запроса.
        updated_at (DateTimeField): Время последнего обновления записи.
    """

    class Status(models.TextChoices):
        """Статусы выполнения задачи анализа."""

        PENDING = "PENDING", "В обработке"
        COMPLETED = "COMPLETED", "Завершено"
        FAILED = "FAILED", "Ошибка"

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="analysis_results",
        verbose_name="Пользователь",
    )
    source_image = models.ImageField(
        upload_to="image_analysis/%Y/%m/%d/",
        verbose_name="Исходное изображение",
    )
    status = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус анализа",
    )
    result_payload = models.JSONField(
        null=True, blank=True, verbose_name="Результат от API"
    )
    error_message = models.TextField(
        null=True, blank=True, verbose_name="Сообщение об ошибке"
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Время создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Время обновления")

    class Meta:
        verbose_name = "Результат анализа изображения"
        verbose_name_plural = "Результаты анализов изображений"
        ordering = ["-created_at"]

    def __str__(self):
        return (
            f"Анализ {self.id} для {self.user.username} ({self.get_status_display()})"
        )
