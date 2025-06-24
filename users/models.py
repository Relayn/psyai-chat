from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Кастомная модель пользователя.

    Наследуется от AbstractUser, что позволяет нам в будущем легко
    добавлять новые поля (например, аватар, телефон), не затрагивая
    встроенную систему аутентификации Django.
    """
    pass


# Create your models here.
