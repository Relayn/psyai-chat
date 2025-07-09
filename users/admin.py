from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """
    Кастомизированное отображение для модели User в админ-панели.
    """

    # важные поля в список для быстрого просмотра.
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "date_joined",
    )
    # фильтры для удобной сегментации пользователей.
    list_filter = ("is_staff", "is_superuser", "is_active", "groups")
    # поиск по ключевым полям.
    search_fields = ("username", "first_name", "last_name", "email")


# Register your models here.
