from django.contrib.auth.models import AbstractUser
from django.db import models

class CustomUser(AbstractUser):
    username = None
    email = models.EmailField(unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    country = models.CharField(max_length=50, blank=True,null=True, verbose_name="Страна"
    )
    token = models.CharField(max_length=100, verbose_name='token', blank=True, null=True)
    is_blocked = models.BooleanField(default=False, verbose_name="Заблокирован")

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        permissions = [
            ("can_block_user", "Может блокировать пользователей"),
            ("can_view_users", "Может просмамтривать пользователей")
        ]

    def __str__(self):
        return self.email
