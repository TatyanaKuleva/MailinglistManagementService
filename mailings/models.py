from django.db import models


class Recipient(models.Model):
    """
       Модель для хранения данных о получателе.
    """
    email = models.EmailField(
        unique=True, help_text="Адрес электронной почты получателя."
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


class Message(models.Model):
    """
    Модель для хранения сообщений, включающая тему и текст письма.
    """
    subject = models.CharField(
        max_length=255,
        verbose_name="Тема письма",
        help_text="Обязательное поле для темы сообщения. Максимум 255 символов."
    )
    body = models.TextField(
        verbose_name="Тело письма",
        blank=True,
        help_text="Основной текст сообщения. Может быть пустым."
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['subject']

    def __str__(self):
        return self.subject

class Mailing(models.Model):
    """
    Модель для управления рассылками.
    Определяет расписание, статус, сообщение и список получателей.
    """

    STATUS_CREATED = 'created'
    STATUS_RUNNING = 'running'
    STATUS_COMPLETED = 'completed'

    STATUS_CHOICES = [
        (STATUS_CREATED, 'Создана'),
        (STATUS_RUNNING, 'Запущена'),
        (STATUS_COMPLETED, 'Завершена'),
    ]

    start_time = models.DateTimeField(
        verbose_name="Дата и время начала рассылки",
        help_text="Укажите дату и время первой отправки рассылки."
    )
    end_time = models.DateTimeField(
        verbose_name="Дата и время окончания рассылки",
        help_text="Укажите дату и время, после которой рассылка не будет отправляться."
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_CREATED,
        verbose_name="Статус рассылки",
        help_text="Текущий статус рассылки (Создана, Запущена, Завершена)."
    )
    message = models.ForeignKey(
        Message,
        on_delete=models.CASCADE,
        related_name='mailings',
        verbose_name="Сообщение",
        help_text="Выберите сообщение, которое будет отправлено в этой рассылке."
    )
    recipients = models.ManyToManyField(
        Recipient,
        related_name='mailings',
        verbose_name="Получатели",
        help_text="Выберите получателей для этой рассылки."
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ['-start_time']

    def __str__(self):
        return f"Рассылка '{self.message.subject}' с {self.start_time.strftime('%Y-%m-%d %H:%M')}"


class MailingAttempt(models.Model):
    """
    Модель для записи каждой попытки отправки конкретной рассылки и ее результата.
    """

    STATUS_SUCCESS = 'success'
    STATUS_FAILED = 'failed'

    STATUS_CHOICES = [
        (STATUS_SUCCESS, 'Успешно'),
        (STATUS_FAILED, 'Не успешно'),
    ]

    timestamp = models.DateTimeField(
        auto_now_add=True,
        verbose_name="Дата и время попытки",
        help_text="Дата и время, когда была предпринята попытка рассылки."
    )
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_FAILED,
        verbose_name="Статус попытки",
        help_text="Результат попытки отправки рассылки (Успешно/Не успешно)."
    )
    server_response = models.TextField(
        blank=True,
        null=True,
        verbose_name="Ответ почтового сервера",
        help_text="Полный или сокращенный ответ, полученный от почтового сервера."
    )
    mailing = models.ForeignKey(
        'Mailing',
        on_delete=models.CASCADE,
        related_name='attempts',
        verbose_name="Рассылка",
        help_text="Ссылка на рассылку, к которой относится эта попытка."
    )


    class Meta:
        verbose_name = "Попытка рассылки"
        verbose_name_plural = "Попытки рассылок"
        ordering = ['-timestamp']

    def __str__(self):
        return f"Попытка '{self.mailing.message.subject}' ({self.status}) в {self.timestamp.strftime('%Y-%m-%d %H:%M')}"

