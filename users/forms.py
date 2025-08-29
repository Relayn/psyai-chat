from django.contrib.auth.forms import UserCreationForm

from .models import User


class CustomUserCreationForm(UserCreationForm):
    """Кастомная форма для создания пользователя."""

    class Meta(UserCreationForm.Meta):  # type: ignore[name-defined]
        model = User
        fields = UserCreationForm.Meta.fields + ("email",)  # type: ignore[attr-defined]
