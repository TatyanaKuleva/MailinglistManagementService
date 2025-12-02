from django.urls import reverse_lazy
from django.views import View
from django.views.generic.edit import CreateView, UpdateView
from .forms import UserRegisterForm, UserProfileEditForm
from django.contrib.auth import get_user_model

User = get_user_model()

class RegisterView(CreateView):
    template_name = 'register.html'
    form_class = UserRegisterForm
    success_url = reverse_lazy('users:login')


