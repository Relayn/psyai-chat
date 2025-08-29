from django.conf import settings
from django.db import models

from users.models import User


class ImageAnalysisResult(models.Model):
    """
    Хранит результат анализа изображения, выполненного через внешний сервис.
    """

    class Status(models.TextChoices):
        PENDING = "PENDING", "В обработке"
        COMPLETED = "COMPLETED", "Завершено"
        FAILED = "FAILED", "Ошибка"

    id: int
    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="analysis_results",
        verbose_name="Пользователь",
    )
    source_image: models.ImageField = models.ImageField(
        upload_to="image_analysis/%Y/%m/%d/",
        verbose_name="Исходное изображение",
    )
    status: models.CharField = models.CharField(
        max_length=20,
        choices=Status.choices,
        default=Status.PENDING,
        verbose_name="Статус анализа",
    )
    result_payload: models.JSONField = models.JSONField(
        null=True, blank=True, verbose_name="Результат от API"
    )
    error_message: models.TextField = models.TextField(
        blank=True, verbose_name="Сообщение об ошибке", default=""
    )
    created_at: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, verbose_name="Время создания"
    )
    updated_at: models.DateTimeField = models.DateTimeField(
        auto_now=True, verbose_name="Время обновления"
    )

    class Meta:
        verbose_name = "Результат анализа изображения"
        verbose_name_plural = "Результаты анализов изображений"
        ordering = ["-created_at"]

    def __str__(self) -> str:
        username = self.user.username if isinstance(self.user, User) else "N/A"
        return f"Анализ {self.id} для {username} ({self.get_status_display()})"

    def get_status_display(self) -> str:
        # Заглушка для mypy, который не видит метод,
        # генерируемый Django для полей с choices.
        ...
