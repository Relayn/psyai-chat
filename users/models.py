from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """
    Кастомная модель пользователя.

    Наследуется от AbstractUser, что позволяет нам в будущем легко
    добавлять новые поля (например, аватар, телефон), не затрагивая
    встроенную систему аутентификации Django.
    """

    # На данный момент мы не добавляем никаких новых полей,
    # но сама модель уже готова к расширению.
    # Пример поля, которое можно будет добавить в будущем:
    # phone_number = models.CharField(max_length=20, blank=True, null=True)
    pass


# Create your models here.
