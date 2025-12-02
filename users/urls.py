from users.apps import UsersConfig
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from users.views import RegisterView

app_name = UsersConfig.name


urlpatterns = [
    path('login/', LoginView.as_view(template_name= 'login.html'), name='login'),
    path('logout/', LogoutView.as_view(template_name='users/logged_out.html', next_page='users:login'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
]
