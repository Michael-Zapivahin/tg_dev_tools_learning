from django.contrib.auth.models import AbstractUser


class User(AbstractUser):
    """Custom user model to extend it with extra fields later."""

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
