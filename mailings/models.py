from django.db import models


class Recipient(models.Model):
    email = models.EmailField(
        unique=True, help_text="Адрес электронной почты подписчика."
    )
    full_name = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        help_text="Полное имя получателя (Ф.И.О.).",
    )
    comment = models.TextField(
        blank=True, null=True, help_text="Дополнительный комментарий о получателе."
    )
    date_added = models.DateTimeField(
        auto_now_add=True, help_text="Дата добавления получателя."
    )

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ["date_added"]
