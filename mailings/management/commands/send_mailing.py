import logging
from mailings.models import Mailing, MailingAttempt
from django.core.management import call_command
from django.core.management.base import BaseCommand, CommandError
from django.utils import timezone
from django.conf import settings
from django.core.mail import send_mail

logger = logging.getLogger('run_mailings')
class Command(BaseCommand):
    """
    Django команда для ручного запуска рассылки сообщений.
    """
    help = 'Запускает рассылку сообщений вручную по ID или все активные рассылки.'

    def add_arguments(self, parser):
        """
        Добавляет аргументы командной строки для команды.
        """
        parser.add_argument(
            '--id',
            type=int,
            help='Укажите ID рассылки для ручного запуска.',
        )
        parser.add_argument(
            '--all-active',
            action='store_true',
            help='Запустить все рассылки, которые активны в текущий момент (start_time <= now <= end_time).',
        )

    def handle(self, *args, **options):
        """
        Основной метод, выполняемый при вызове команды.
        """
        mailing_id = options.get('id')
        run_all_active = options.get('all_active')

        if mailing_id:
            try:
                mailing = Mailing.objects.get(pk=mailing_id)
                self._process_single_mailing(mailing)
            except Mailing.DoesNotExist:
                raise CommandError(f'Рассылка с ID {mailing_id} не найдена.')
        elif run_all_active:
            now = timezone.now()
            active_mailings = Mailing.objects.filter(
                start_time__lte=now,
                end_time__gte=now
            )
            if not active_mailings.exists():
                self.stdout.write(self.style.WARNING('Нет активных рассылок для запуска.'))
                return

            self.stdout.write(
                self.style.SUCCESS(f'Найдено {active_mailings.count()} активных рассылок для обработки.'))
            for mailing in active_mailings:
                self.stdout.write(self.style.HTTP_INFO(
                    f'\n--- Обработка рассылки ID: {mailing.pk} (Тема: "{mailing.message.subject}") ---'))
                self._process_single_mailing(mailing)
                self.stdout.write(self.style.HTTP_INFO(f'--- Завершено для рассылки ID: {mailing.pk} ---'))
        else:
            raise CommandError('Пожалуйста, укажите либо `--id <ID_рассылки>`, либо `--all-active`.')

    def _process_single_mailing(self, mailing):
        """
        Внутренний метод для обработки одной рассылки.
        Повторяет логику метода `send_mailing_manually`.
        """
        self.stdout.write(self.style.SUCCESS(
            f"Начало ручной отправки рассылки ID:{mailing.pk}, Тема: '{mailing.message.subject}'"))
        logger.info(f"Начало ручной отправки рассылки ID:{mailing.pk}, Тема: '{mailing.message.subject}'")

        now = timezone.now()

        if not (mailing.start_time <= now <= mailing.end_time):
            message = (f"Ошибка: Невозможно запустить рассылку '{mailing.message}'. "
                       f"Текущее время {now.strftime('%Y-%m-%d %H:%M:%S')} "
                       f"не находится между {mailing.start_time.strftime('%Y-%m-%d %H:%M:%S')} "
                       f"и {mailing.end_time.strftime('%Y-%m-%d %H:%M:%S')}.")
            self.stderr.write(self.style.ERROR(message))
            logger.warning(f"Валидация времени для рассылки ID:{mailing.pk} не пройдена: {message}")
            return False


        if not mailing.recipients.exists():
            message = f"Ошибка: Рассылка '{mailing.message}' не имеет получателей."
            self.stderr.write(self.style.ERROR(message))
            logger.warning(f'Для рассылки ID:{mailing.pk} не найдено получателей.')
            return False

        self.stdout.write(self.style.NOTICE(f"Валидация для рассылки ID:{mailing.pk} пройдена. Начинается отправка писем."))
        logger.info(f"Валидация для рассылки ID:{mailing.pk} пройдена. Начинается отправка писем.")

        successful_sends = 0
        failed_sends = 0


        for recipient in mailing.recipients.all():
            logger.debug(f"Попытка отправить письмо клиенту {recipient.email} для рассылки ID:{mailing.pk}")
            try:
                send_mail(
                    subject=mailing.message.subject,
                    message=mailing.message.body,
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[recipient.email],
                    fail_silently=False,
                    )

                MailingAttempt.objects.create(
                    mailing=mailing,
                    status=MailingAttempt.STATUS_SUCCESS,
                    timestamp=timezone.now(),
                    server_response=None
                )
                successful_sends += 1
                self.stdout.write(self.style.MIGRATE_SUCCESS(f"Успешно отправлено клиенту {recipient.email} для рассылки ID:{mailing.pk}."))
                logger.info(f"Успешно отправлено клиенту {recipient.email} для рассылки ID:{mailing.pk}.")

            except Exception as e:
                MailingAttempt.objects.create(
                    mailing=mailing,
                    status=MailingAttempt.STATUS_FAILED,
                    timestamp=timezone.now(),
                    server_response=str(e)
                )
                failed_sends += 1
                self.stderr.write(self.style.ERROR(f"Ошибка отправки клиенту {recipient.email} для рассылки ID:{mailing.pk}: {e}"))
                logger.error(f"Ошибка отправки клиенту {recipient.email} для рассылки ID:{mailing.pk}: {e}")


        mailing.update_status()
        mailing.save()

        final_message = (f"🎉 Рассылка '{mailing.message}' завершена: "
                         f"Успешно отправлено: {successful_sends}, "
                         f"Неудачных отправок: {failed_sends}.")
        self.stdout.write(self.style.SUCCESS(final_message))
        logger.info(final_message)
        return True




