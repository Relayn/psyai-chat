from django.contrib.auth.forms import UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Кастомная форма для создания пользователя."""

    class Meta(UserCreationForm.Meta):
        model = User
        # Правильный способ: берем поля из родительской формы
        # и добавляем к ним наши собственные.
        fields = UserCreationForm.Meta.fields + ("email",)
