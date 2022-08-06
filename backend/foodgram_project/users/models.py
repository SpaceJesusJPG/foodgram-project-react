from django.contrib.auth.models import AbstractUser
from django.db import models

USER = "user"
ADMIN = "admin"

CHOICES = ((USER, "user"), (ADMIN, "admin"))


class User(AbstractUser):
    username = models.CharField(
        max_length=150, unique=True, blank=False, null=False
    )
    email = models.EmailField(
        "Электронная почта",
        max_length=254,
        unique=True,
        blank=False,
        null=False,
    )
    role = models.CharField(
        "Роль", max_length=10, choices=CHOICES, default=USER, blank=True
    )
    first_name = models.CharField(
        "Имя пользователя", max_length=150, null=False
    )
    last_name = models.CharField(
        "Фамилия пользователя", max_length=150, null=False
    )

    class Meta:
        verbose_name = "Пользователь"
        verbose_name_plural = "Пользователи"

    @property
    def is_user(self):
        return self.role == USER

    @property
    def is_admin(self):
        return self.is_superuser is True or self.role == ADMIN


class Subscription(models.Model):
    subscriber = models.ForeignKey(
        User, related_name="subscriber", on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        User, related_name="subscribing_to", on_delete=models.CASCADE
    )
