from django.contrib import messages
from django.core.mail import send_mail
from django.utils import timezone


def send_mailing(mailing_id):
    from .models import Mailing, MailingAttempt

    mailing = Mailing.objects.get(id=mailing_id)
    clients = mailing.recipients.all()

    for client in clients:
        try:
            send_mail(
                subject=mailing.subject,
                message=mailing.body,
                from_email="no-reply@example.com",
                recipient_list=[client.email],
                fail_silently=False,
            )
            MailingAttempt.objects.create(
                mailing=mailing,
                client=client,
                status="success",
                smtp_response="Сообщение отправлено успешно",
                timestamp=timezone.now(),
            )

        except Exception as e:
            MailingAttempt.objects.create(
                mailing=mailing,
                client=client,
                status="failed",
                smtp_response=str(e),
                timestamp=timezone.now(),
            )

        messages.success("Рассыдка успешно отправлена.")
