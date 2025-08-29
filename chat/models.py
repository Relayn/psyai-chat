from django.conf import settings
from django.db import models

from users.models import User


class ChatSession(models.Model):
    id: int
    user: models.ForeignKey = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions",
        verbose_name="Пользователь",
    )
    start_time: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, verbose_name="Время начала"
    )
    message_count: models.PositiveIntegerField = models.PositiveIntegerField(
        default=0, verbose_name="Количество сообщений"
    )
    messages: "models.Manager[ChatMessage]"

    class Meta:
        verbose_name = "Сессия чата"
        verbose_name_plural = "Сессии чата"
        ordering = ["-start_time"]

    def __str__(self) -> str:
        username = self.user.username if isinstance(self.user, User) else "N/A"
        start_str = self.start_time.strftime("%Y-%m-%d %H:%M")
        return f"Сессия {username} от {start_str}"


class ChatMessage(models.Model):
    class SenderType(models.TextChoices):
        USER = "USER", "Пользователь"
        AI = "AI", "Искусственный интеллект"

    id: int
    session: models.ForeignKey = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Сессия",
    )
    text: models.TextField = models.TextField(verbose_name="Текст сообщения")
    timestamp: models.DateTimeField = models.DateTimeField(
        auto_now_add=True, verbose_name="Время отправки"
    )
    sender_type: models.CharField = models.CharField(
        max_length=4,
        choices=SenderType.choices,
        verbose_name="Тип отправителя",
    )

    class Meta:
        verbose_name = "Сообщение чата"
        verbose_name_plural = "Сообщения чата"
        ordering = ["timestamp"]

    def __str__(self) -> str:
        return (
            f"{self.get_sender_type_display()} в {self.timestamp.strftime('%H:%M:%S')}"
        )

    def get_sender_type_display(self) -> str:
        # Заглушка для mypy, который не видит метод,
        # генерируемый Django для полей с choices.
        ...
