from django.views.generic.edit import CreateView, UpdateView
from .forms import UserRegisterForm, UserProfileEditForm
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse_lazy, reverse
from django.core.mail import send_mail
from config.settings import EMAIL_HOST_USER
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
import secrets
from .forms import UserRegisterForm, UserProfileEditForm


User = get_user_model()

class RegisterView(CreateView):
    template_name = 'register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')


    def form_valid(self, form):
        user = form.save()
        user.is_active=False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f'http//{host}/users/email-confirm/{token}'
        send_mail(
            subject = 'Подтверждение почты',
            message = f'Перейди по ссылке для подвтерждения почты {url}',
            from_email = EMAIL_HOST_USER,
            recipient_list = [user.email]
        )
        messages.success(self.request, 'Вам на почту отправлено письмо для подтверждения аккаунта.')
        return super().form_valid(form)

def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    send_mail(
        subject='Добро пожаловать в cервис управления рассылками!',
        message=f'Привет, {user.email}!\n\nДобро пожаловать  cервис управления рассылкам! Ваш аккаунт успешно активирован. Теперь вы можете войти в систему и начать рассылки.\n\nС уважением,\nКоманда  Skystore',
        from_email=EMAIL_HOST_USER,
        recipient_list=[user.email]
    )
    messages.success(request, 'Ваша почта успешно подтверждена! Добро пожаловать!')
    return redirect(reverse('users:login'))

class UserProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileEditForm
    template_name = 'users/profile_edit.html'
    success_url = reverse_lazy('users:profile_edit')

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, 'Ваш профиль успешно обновлен!')
        return super().form_valid(form)
