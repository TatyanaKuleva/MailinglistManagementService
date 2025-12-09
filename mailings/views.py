from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.shortcuts import render
from django.contrib import messages
from django.shortcuts import redirect, get_object_or_404
from django.urls import reverse
from django.views.generic import (
    ListView,
    DetailView,
    CreateView,
    UpdateView,
    DeleteView,
    View
)
from django.urls import reverse_lazy
from .models import Recipient, Message, Mailing, MailingAttempt
from .forms import RecipientForm, MessageForm, MailingForm
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin, PermissionRequiredMixin
from django.http import HttpResponse, Http404, HttpResponseForbidden



def is_manager(user):
    return user.groups.filter(name='Менеджеры').exists()


@login_required
def home_view(request):
    """
    Отображает главную страницу с показателями рассылок и клиентов.
    """
    now = timezone.now()
    user = request.user

    total_mailings_count = Mailing.objects.filter(owner=user).count()

    active_mailings_count = Mailing.objects.filter(
        owner=user,
        start_time__lte=now,
        end_time__gte=now,
        status= 'running'
    ).count()


    unique_recipients_count = Recipient.objects.filter(owner=user).count()

    context = {
        'total_mailings_count': total_mailings_count,
        'active_mailings_count': active_mailings_count,
        'unique_recipients_count': unique_recipients_count,
    }

    return render(request, 'mailings/home.html', context)

@login_required
def statistic_view(request):
    """
    Отображает страницу cо статистикой рассылок пользователя.
    """
    now = timezone.now()
    user = request.user

    total_success_mailings = MailingAttempt.objects.filter(owner=user, status = 'success').count()
    total_failed_mailings = MailingAttempt.objects.filter(owner=user, status='failed').count()
    total_send_message = MailingAttempt.objects.filter(owner=user).count()




    context = {
        'total_success_mailings': total_success_mailings,
        'total_failed_mailing': total_failed_mailings,
        'total_send_message': total_send_message,
    }

    return render(request, 'mailings/statistic_page.html', context)


class RecipientListView(ListView):
    model = Recipient
    template_name = 'mailings/recipient_list.html'
    context_object_name = 'recipients'

    def get_queryset(self):
        user = self.request.user
        if user.has_perm('view_all_recipient'):
            return Recipient.objects.all()
        else:
            return Recipient.objects.filter(owner=user)

class RecipientDetailView(DetailView):
    model = Recipient
    template_name = 'mailings/recipient_detail.html'
    context_object_name = 'recipient'


class RecipientCreateView(LoginRequiredMixin, UserPassesTestMixin, CreateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    success_url = reverse_lazy('mailings:recipient_list')

    def test_func(self):
        user = self.request.user
        return not user.groups.filter(name='Менеджеры').exists()

    def handle_no_permission(self):
        return HttpResponseForbidden("У вас нет прав для создания получателей.")


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class RecipientUpdateView(UpdateView):
    model = Recipient
    form_class = RecipientForm
    template_name = 'mailings/recipient_form.html'
    context_object_name = 'recipient'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.owner != self.request.user or is_manager(self.request.user):
            return HttpResponseForbidden("У вас нет разрешения на редактирование получателей.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('mailings:recipient_detail', kwargs={'pk': self.object.pk})


class RecipientDeleteView(DeleteView):
    model = Recipient
    template_name = 'mailings/recipient_confirm_delete.html'
    success_url = reverse_lazy('mailings:recipient_list')
    context_object_name = 'recipient'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.owner != self.request.user or is_manager(self.request.user):
            return HttpResponseForbidden("У вас нет разрешения на удаление получателей.")
        return super().dispatch(request, *args, **kwargs)

@method_decorator(cache_page(60 * 15), name='dispatch')
class MessageListView(ListView):
    model = Message
    template_name = 'mailings/message_list.html'
    context_object_name = 'messages'

    def get_queryset(self):
        user = self.request.user
        if user.has_perm('view_all_message'):
            return Message.objects.all()
        else:
            return Message.objects.filter(owner=user)


class MessageDetailView(DetailView):
    model = Message
    template_name = 'mailings/message_detail.html'
    context_object_name = 'message'


class MessageCreateView(LoginRequiredMixin,  UserPassesTestMixin, CreateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    success_url = reverse_lazy('mailings:message_list')

    def test_func(self):
        user = self.request.user
        return not user.groups.filter(name='Менеджеры').exists()

    def handle_no_permission(self):
        return HttpResponseForbidden("У вас нет прав для создания сообщений")

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MessageUpdateView(UpdateView):
    model = Message
    form_class = MessageForm
    template_name = 'mailings/message_form.html'
    context_object_name = 'message'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.owner != self.request.user or is_manager(self.request.user):
            return HttpResponseForbidden("У вас нет разрешения на редактирование сообщений.")
        return super().dispatch(request, *args, **kwargs)


    def get_success_url(self):
        return reverse_lazy('mailings:message_detail', kwargs={'pk': self.object.pk})


class MessageDeleteView(DeleteView):
    model = Message
    template_name = 'mailings/message_confirm_delete.html'
    success_url = reverse_lazy('mailings:message_list')
    context_object_name = 'message'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.owner != self.request.user or is_manager(self.request.user):
            return HttpResponseForbidden("У вас нет разрешения на удаление сообщений.")
        return super().dispatch(request, *args, **kwargs)

@method_decorator(cache_page(60 * 15), name='dispatch')
class MailingListView(LoginRequiredMixin, ListView):
    model = Mailing
    template_name = 'mailings/mailing_list.html'
    context_object_name = 'mailings'

    def get_queryset(self):
        user = self.request.user
        if user.has_perm('view_all_mailing'):
            return Mailing.objects.all()
        else:
            return Mailing.objects.filter(owner=user)


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



class MailingCreateView(LoginRequiredMixin,  UserPassesTestMixin, CreateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    success_url = reverse_lazy('mailings:mailing_list')

    def test_func(self):
        user = self.request.user
        return not user.groups.filter(name='Менеджеры').exists()

    def handle_no_permission(self):
        return HttpResponseForbidden("У вас нет прав для создания рассылок.")


    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs


    def form_valid(self, form):
        form.instance.owner = self.request.user
        return super().form_valid(form)


class MailingUpdateView(UpdateView):
    model = Mailing
    form_class = MailingForm
    template_name = 'mailings/mailing_form.html'
    context_object_name = 'mailing'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.owner != self.request.user or is_manager(self.request.user):
            return HttpResponseForbidden("У вас нет разрешения на редактирование этой рассылки.")
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy('mailings:mailing_detail', kwargs={'pk': self.object.pk})


class MailingDeleteView(DeleteView):
    model = Mailing
    template_name = 'mailings/mailing_confirm_delete.html'
    success_url = reverse_lazy('mailings:mailing_list')
    context_object_name = 'mailing'

    def dispatch(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.owner != self.request.user or is_manager(self.request.user):
            return HttpResponseForbidden("У вас нет разрешения на удаление этой рассылки.")
        return super().dispatch(request, *args, **kwargs)


@method_decorator(cache_page(60 * 15), name='dispatch')
class MailingAttemptListView(ListView):
    model = MailingAttempt
    template_name = 'mailings/mailing_attempt_list.html'
    context_object_name = 'mailing_attempts'

    def get_queryset(self):
        user = self.request.user
        if user.has_perm('view_all_mailing_attempt'):
            return MailingAttempt.objects.all()
        else:
            return MailingAttempt.objects.filter(owner=user)

class MailingAttemptDetailView(DetailView):
    model = MailingAttempt
    template_name = 'mailings/mailing_attempt_detail.html'
    context_object_name = 'mailing_attempt'

class MailingToggleStatusView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = Mailing
    fields = ['in_active_status']
    template_name = 'mailings/mailing_toggle_status_confirm.html'
    success_url = reverse_lazy('mailings:mailing_list')
    permission_required = 'mailings.disable_mailing'

    def get_object(self, queryset=None):
        return get_object_or_404(Mailing, pk=self.kwargs['pk'])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['current_status'] = self.object.in_active_status
        context['new_status_action'] = 'отключить' if self.object.in_active_status == 'active' else 'включить'
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.in_active_status == 'active':
            new_status = 'inactive'
        elif self.object.in_active_status == 'inactive':
            new_status = 'active'
        else:
            return redirect(self.success_url)


        self.object.in_active_status = new_status
        self.object.save()

        return redirect(self.success_url)








