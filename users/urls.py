from users.apps import UsersConfig
from django.urls import path
from django.contrib.auth.views import LoginView, LogoutView
from users.views import RegisterView, UserProfileEditView, email_verification

app_name = UsersConfig.name


urlpatterns = [
    path('login/', LoginView.as_view(template_name= 'login.html', next_page='mailings:home'), name='login'),
    path('logout/', LogoutView.as_view(template_name='users/logged_out.html', next_page='users:login'), name='logout'),
    path('register/', RegisterView.as_view(), name='register'),
    path('email-confirm/<str:token>/', email_verification, name='email-confirm'),
    path('profile/edit/', UserProfileEditView.as_view(), name='profile_edit')
]


