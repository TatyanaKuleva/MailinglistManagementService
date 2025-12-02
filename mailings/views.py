from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect
from django.urls import reverse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView
)
from django.urls import reverse_lazy
from .models import Recipient, Message, Mailing, MailingAttempt
from .forms import RecipientForm, MessageForm, MailingForm
from .services import send_mailing
import logging




class RecipientListView(ListView):
    model = Recipient
    template_name = 'mailings/recipient_list.html'
    context_object_name = 'recipients'


class RecipientDetailView(DetailView):
    model = Recipient
    template_name = 'mailings/recipient_detail.html'
    context_object_name = 'recipient'


class RecipientCreateView(CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:recipient_list')


class RecipientUpdateView(UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    context_object_name = 'recipient'

    def get_success_url(self):
        return reverse_lazy('mailings:recipient_detail', kwargs={'pk': self.object.pk})


class RecipientDeleteView(DeleteView):
    model = Recipient
    template_name = 'mailings/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailings:recipient_list')
    context_object_name = 'recipient'


class MessageListView(ListView):
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'


class MessageDetailView(DetailView):
    model = Message
    template_name = 'mailings/message_detail.html'
    context_object_name = 'message'


class MessageCreateView(CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    context_object_name = 'message'

    def get_success_url(self):
        return reverse_lazy('mailings:message_detail', kwargs={'pk': self.object.pk})


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('mailings:message_list')
    context_object_name = 'message'

class MailingListView(ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'


class MailingDetailView(DetailView):
    model = Mailing
    template_name = 'mailings/mailing_detail.html'
    context_object_name = 'mailing'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        mailing = self.get_object()

        context['recipients_count'] = mailing.recipients.count()
        context['recipients'] = mailing.recipients.all()
        return context


    def post(self, request, *args, **kwargs):
        """
        Обрабатывает POST-запрос при нажатии кнопки "Отправить".
        """
        self.object = self.get_object()

        if 'send_mailing' in request.POST:
            is_sent, messages_text = self.object.send_mailing_manually()


            if is_sent:
                messages.success(request, f"Рассылка успешно отправлена!{messages_text}")
            else:
                messages.error(request, f" Ошибка при отправке рассылки {messages_text}")




            return redirect(reverse('mailings:mailing_detail', kwargs={'pk': self.object.pk}))


        return super().post(request, *args, **kwargs)



class MailingCreateView(CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    context_object_name = 'mailing'

    def get_success_url(self):
        return reverse_lazy('mailings:mailing_detail', kwargs={'pk': self.object.pk})


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:mailing_list')
    context_object_name = 'mailing'

class MailingAttemptListView(ListView):
    model = MailingAttempt
    template_name = 'mailings/mailing_attempt_list.html'
    context_object_name = 'mailing_attempts'


class MailingAttemptDetailView(DetailView):
    model = MailingAttempt
    template_name = 'mailings/mailing_attempt_detail.html'
    context_object_name = 'mailing_attempt'




