import secrets

from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin, UserPassesTestMixin
from django.core.mail import send_mail
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.views.generic import ListView
from django.views.generic.edit import CreateView, UpdateView

from config.settings import EMAIL_HOST_USER

from .forms import UserProfileEditForm, UserRegisterForm
from .models import CustomUser

User = get_user_model()


def is_manager(user):
    return user.groups.filter(name="Менеджеры").exists()


class RegisterView(CreateView):
    template_name = "register.html"
    form_class = UserRegisterForm
    success_url = reverse_lazy("users:login")

    def form_valid(self, form):
        user = form.save()
        user.is_active = False
        token = secrets.token_hex(16)
        user.token = token
        user.save()
        host = self.request.get_host()
        url = f"http//{host}/users/email-confirm/{token}"
        send_mail(
            subject="Подтверждение почты",
            message=f"Перейди по ссылке для подвтерждения почты {url}",
            from_email=EMAIL_HOST_USER,
            recipient_list=[user.email],
        )
        messages.success(self.request, "Вам на почту отправлено письмо для подтверждения аккаунта.")
        return super().form_valid(form)


def email_verification(request, token):
    user = get_object_or_404(User, token=token)
    user.is_active = True
    user.save()
    send_mail(
        subject="Добро пожаловать в cервис управления рассылками!",
        message=f"Привет, {user.email}!\n\nДобро пожаловать  cервис управления рассылкам! Ваш аккаунт успешно "
                f"активирован. Теперь вы можете войти в систему и начать рассылки.\n\nС уважением,\nКоманда  Skystore",
        from_email=EMAIL_HOST_USER,
        recipient_list=[user.email],
    )
    messages.success(request, "Ваша почта успешно подтверждена! Добро пожаловать!")
    return redirect(reverse("users:login"))


class UserProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    form_class = UserProfileEditForm
    template_name = "users/profile_edit.html"
    success_url = reverse_lazy("users:profile_edit")

    def get_object(self, queryset=None):
        return self.request.user

    def form_valid(self, form):
        messages.success(self.request, "Ваш профиль успешно обновлен!")
        return super().form_valid(form)


class UsersListView(UserPassesTestMixin, ListView):
    model = CustomUser
    template_name = "users/users_list.html"
    context_object_name = "users"
    permission_required = "users.can_view_users"

    def test_func(self):
        user = self.request.user
        return user.groups.filter(name="Менеджеры").exists()

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            return HttpResponseForbidden("У вас нет прав для просмотра списка пользователей")
        return super().handle_no_permission()

    def get_queryset(self):
        return super().get_queryset()


class ToggleUserBlockView(LoginRequiredMixin, PermissionRequiredMixin, UpdateView):
    model = CustomUser
    fields = ["is_blocked"]
    template_name = "users/users_toggle_status_confirm.html"
    success_url = reverse_lazy("users:users_list")
    permission_required = "users.can_block_user"

    def get_object(self, queryset=None):
        return get_object_or_404(CustomUser, pk=self.kwargs["pk"])

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["current_status"] = "заблокирован" if self.object.is_blocked else "активен"
        context["new_status_action"] = "разблокировать" if self.object.is_blocked else "заблокировать"
        return context

    def post(self, request, *args, **kwargs):
        self.object = self.get_object()
        if self.object.is_blocked:
            new_status = False
        else:
            new_status = True

        self.object.is_blocked = new_status
        self.object.save()

        return redirect(self.success_url)
