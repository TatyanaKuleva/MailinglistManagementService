from django.urls import path
from .views import (
    RecipientListView,
    RecipientDetailView,
    RecipientCreateView,
    RecipientUpdateView,
    RecipientDeleteView,
    MessageListView,
    MessageCreateView,
    MessageDetailView,
    MessageUpdateView,
    MessageDeleteView,
    MailingListView,
    MailingDetailView,
    MailingCreateView,
    MailingUpdateView,
    MailingDeleteView,
    MailingAttemptListView,
    MailingAttemptDetailView,
    MailingToggleStatusView,
    home_view,
    statistic_view,
)

app_name = 'mailings'

urlpatterns = [
    path("home/", home_view, name="home"),
    path("statistic/", statistic_view, name="statistic"),
    path('recipients/', RecipientListView.as_view(), name='recipient_list'),
    path('recipient/create/', RecipientCreateView.as_view(), name='recipient_create'),
    path('recipient/<int:pk>/', RecipientDetailView.as_view(), name='recipient_detail'),
    path('recipient/<int:pk>/update/', RecipientUpdateView.as_view(), name='recipient_update'),
    path('recipient/<int:pk>/delete/', RecipientDeleteView.as_view(), name='recipient_delete'),
    path('messages/', MessageListView.as_view(), name='message_list'),
    path('message/create/', MessageCreateView.as_view(), name='message_create'),
    path('message/<int:pk>/', MessageDetailView.as_view(), name='message_detail'),
    path('message/<int:pk>/update/', MessageUpdateView.as_view(), name='message_update'),
    path('message/<int:pk>/delete/', MessageDeleteView.as_view(), name='message_delete'),
    path('mailings/', MailingListView.as_view(), name='mailing_list'),
    path('mailing/<int:pk>/', MailingDetailView.as_view(), name='mailing_detail'),
    path('mailing/create/', MailingCreateView.as_view(), name='mailing_create'),
    path('mailing/<int:pk>/update/', MailingUpdateView.as_view(), name='mailing_update'),
    path('mailing/<int:pk>/delete/', MailingDeleteView.as_view(), name='mailing_delete'),
    path('mailing_attempts/', MailingAttemptListView.as_view(), name='mailing_attempts_list'),
    path('mailing_attempts/<int:pk>/', MailingAttemptDetailView.as_view(), name='mailing_attempt_detail'),
    path('mailings/<int:pk>/toggle-status/', MailingToggleStatusView.as_view(), name='mailing_toggle_status')

]