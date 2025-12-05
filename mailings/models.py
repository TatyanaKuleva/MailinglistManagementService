from django.db import models
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.core.mail import send_mail
from config.settings import EMAIL_HOST_USER
import logging
from users.models import CustomUser


logger = logging.getLogger('mailings.models')


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
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Владелец",
        help_text="Укажите создателя",
        related_name="recipients",
    )

    def __str__(self):
        return self.email

    class Meta:
        verbose_name = "Получатель"
        verbose_name_plural = "Получатели"
        ordering = ["date_added"]
        permissions = [
            ("view_all_recipient", "Может просматривать всех получателей (менеджер)"),
        ]


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
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Владелец",
        help_text="Укажите создателя",
        related_name="message",
    )

    class Meta:
        verbose_name = "Сообщение"
        verbose_name_plural = "Сообщения"
        ordering = ['subject']
        permissions = [
            ("view_all_message", "Может просматривать все сообщения (менеджер)"),
        ]

    def __str__(self):
        return self.subject

class Mailing(models.Model):
    """
    Модель для управления рассылками.
    Определяет расписание, статус рассылки, сообщение и список получателей.
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
        verbose_name="Дата и время c какого момента рассылка может быть запущена",
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
    owner = models.ForeignKey(
        CustomUser,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        verbose_name="Владелец",
        help_text="Укажите создателя",
        related_name="mailing",
    )

    class Meta:
        verbose_name = "Рассылка"
        verbose_name_plural = "Рассылки"
        ordering = ['-start_time']
        permissions = [
            ("view_all_mailing", "Может просматривать все рассылки (менеджер)"),
            ("disable_mailing", "Может отключать рассылки (менеджер)"),

        ]

    def __str__(self):
        return f"Рассылка '{self.message.subject}' с {self.start_time.strftime('%Y-%m-%d %H:%M:%S')}, статус {self.status}"

    def clean(self):
        """
        Метод для кастомной валидации полей модели.
        """
        super().clean()

        now = timezone.now()
        if self.start_time and self.start_time < now:
            raise ValidationError(
                {'start_time': 'Дата и время начала рассылки не могут быть в прошлом.'}
            )

        if self.start_time and self.end_time and self.start_time >= self.end_time:
            raise ValidationError(
                {'end_time': 'Дата и время окончания рассылки должны быть позже даты начала.'}
            )


    def update_status(self):
        """
        Обновляет статус рассылки на основе текущего времени.
        Возвращает True, если статус был изменен, иначе False.
        """
        now = timezone.now()

        new_status = self.status


        if now < self.start_time:
            new_status = self.STATUS_CREATED
        elif self.start_time <= now <= self.end_time:
            new_status = self.STATUS_RUNNING
        elif now > self.end_time:
            new_status = self.STATUS_COMPLETED

        if new_status != self.status:
            self.status = new_status
            self.save(update_fields=['status'])
            return True

        return False

    def send_mailing_manually(self):
        """
        Запускает рассылку вручную.
        Возвращает True в случае успешного начала отправки, False при ошибке валидации времени.
        """
        logger.info(f"Начало ручной отправки рассылки ID:{self.pk}, Тема: '{self.message.subject}'")
        now = timezone.now()

        if not (self.start_time <= now <= self.end_time):
            message = (f"Ошибка: Невозможно запустить рассылку '{self.message}'. "
                       f"Текущее время {now.strftime('%Y-%m-%d %H:%M:%S')} "
                       f"не находится между {self.start_time.strftime('%Y-%m-%d %H:%M:%S')} "
                       f"и {self.end_time.strftime('%Y-%m-%d %H:%M:%S')}.")

            logger.warning(f"Валидация времени для рассылки ID:{self.pk} не пройдена: {message}")
            return False, message

        if not self.recipients.exists():
            message = f"Ошибка: Рассылка '{self.message}' не имеет получателей."
            logger.warning(f'Для рассылки ID:{self.pk} не найдено получателей.')
            return False, message

        logger.info(f"Валидация для рассылки ID:{self.pk} пройдена. Начинается отправка писем.")


        successful_sends = 0
        failed_sends = 0



        for recipient in self.recipients.all():
            logger.debug(f"Попытка отправить письмо клиенту {recipient.email} для рассылки ID:{self.pk}")
            try:
                send_mail(
                    subject=self.message.subject,
                    message=self.message.body,
                    from_email=EMAIL_HOST_USER,
                    recipient_list=[recipient.email],
                    fail_silently=False
                        )
                MailingAttempt.objects.create(
                        mailing=self,
                        status= MailingAttempt.STATUS_SUCCESS,
                        timestamp=timezone.now(),
                        server_response = None
                    )
                successful_sends += 1
                logger.info(f"Успешно отправлено клиенту {recipient.email} для рассылки ID:{self.pk}.")
            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=self,
                    status=MailingAttempt.STATUS_FAILED,
                    timestamp=timezone.now(),
                    server_response=str(e)
                )
                failed_sends += 1
                logger.error(f"Ошибка отправки клиенту {recipient.email} для рассылки ID:{self.pk}: {e}")

            self.update_status()
            self.save()

        final_message = (f"Рассылка '{self.message}' завершена: ")

        logger.info(f"{final_message}")
        return True, final_message



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

