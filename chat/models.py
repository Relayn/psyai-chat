from django.conf import settings
from django.db import models


class ChatSession(models.Model):
    """
    Модель сессии чата.

    Хранит информацию о каждой отдельной сессии чата между
    пользователем и ИИ.

    Attributes:
        user (ForeignKey): Ссылка на пользователя, начавшего сессию.
        start_time (DateTimeField): Время начала сессии.
        message_count (PositiveIntegerField): Количество сообщений в сессии.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="chat_sessions",
        verbose_name="Пользователь",
    )
    start_time = models.DateTimeField(
        auto_now_add=True, verbose_name="Время начала"
    )
    message_count = models.PositiveIntegerField(
        default=0, verbose_name="Количество сообщений"
    )

    class Meta:
        verbose_name = "Сессия чата"
        verbose_name_plural = "Сессии чата"
        ordering = ["-start_time"]

    def __str__(self):
        return f"Сессия {self.user.username} от {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class ChatMessage(models.Model):
    """
    Модель сообщения в чате.

    Хранит текст сообщения, его отправителя и время создания.

    Attributes:
        session (ForeignKey): Ссылка на сессию, к которой относится сообщение.
        text (TextField): Текст сообщения.
        timestamp (DateTimeField): Время отправки сообщения.
        sender_type (CharField): Тип отправителя (Пользователь или ИИ).
    """

    class SenderType(models.TextChoices):
        """Перечисление для определения типа отправителя."""

        USER = "USER", "Пользователь"
        AI = "AI", "Искусственный интеллект"

    session = models.ForeignKey(
        ChatSession,
        on_delete=models.CASCADE,
        related_name="messages",
        verbose_name="Сессия",
    )
    text = models.TextField(verbose_name="Текст сообщения")
    timestamp = models.DateTimeField(
        auto_now_add=True, verbose_name="Время отправки"
    )
    sender_type = models.CharField(
        max_length=4,
        choices=SenderType.choices,
        verbose_name="Тип отправителя",
    )

    class Meta:
        verbose_name = "Сообщение чата"
        verbose_name_plural = "Сообщения чата"
        ordering = ["timestamp"]

    def __str__(self):
        return f"{self.get_sender_type_display()} в {self.timestamp.strftime('%H:%M:%S')}"


from django.db import models

# Create your models here.
