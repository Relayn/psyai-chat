from django.contrib import admin

from .models import ChatMessage, ChatSession


@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):
    """
    Настройки отображения для модели ChatSession в админ-панели.
    """

    list_display = ("id", "user", "start_time", "message_count")
    list_filter = ("start_time", "user")
    search_fields = ("user__username",)
    ordering = ("-start_time",)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    """
    Настройки отображения для модели ChatMessage в админ-панели.
    """

    list_display = ("session_id", "user", "sender_type", "text_preview", "timestamp")
    list_filter = ("timestamp", "sender_type", "session__user")
    search_fields = ("text", "session__user__username")
    ordering = ("-timestamp",)

    @admin.display(description="Текст (начало)")
    def text_preview(self, obj):
        """Возвращает первые 50 символов сообщения."""
        return obj.text[:50] + "..." if len(obj.text) > 50 else obj.text

    @admin.display(description="ID Сессии", ordering="session__id")
    def session_id(self, obj):
        return obj.session.id

    @admin.display(description="Пользователь", ordering="session__user")
    def user(self, obj):
        return obj.session.user