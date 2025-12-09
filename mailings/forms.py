from django import forms
from .models import Recipient, Message, Mailing

class RecipientForm(forms.ModelForm):
    """
    Форма для создания и редактирования объектов модели Получатель.
    """
    class Meta:
        model = Recipient
        fields = ['email', 'full_name', 'comment']
        widgets = {
            'email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Введите email'}),
            'full_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите Ф. И. О.'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Добавьте комментарий (необязательно)'}),
        }
        labels = {
            'email': 'Email',
            'full_name': 'Ф. И. О.',
            'comment': 'Комментарий',
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

class MessageForm(forms.ModelForm):
    """
    Форма для создания и редактирования объектов модели Сообщение.
    """
    class Meta:
        model = Message
        fields = ['subject', 'body']
        widgets = {
            'subject': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Введите тему сообщения'}),
            'body': forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Добавьте текст сообщения'}),
        }
        labels = {
            'subject': 'Тема сообщения',
            'body': 'Текст сообщения',
        }

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)


class MailingForm(forms.ModelForm):
    """
    Форма для создания и редактирования объектов модели Рассылка.
    """
    class Meta:
        model = Mailing
        fields = ['start_time', 'end_time', 'message', 'recipients']
        widgets = {
            'start_time': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'end_time': forms.DateTimeInput(
                attrs={
                    'class': 'form-control',
                    'type': 'datetime-local'
                },
                format='%Y-%m-%dT%H:%M'
            ),
            'message': forms.Select(attrs={'class': 'form-control'}),
            'recipients': forms.SelectMultiple(attrs={'class': 'form-control'}),
        }
        labels = {
            'start_time': 'Дата и время первой отправки',
            'end_time': 'Дата и время окончания отправки ',
            'message': 'Сообщение',
            'recipients': 'Получатели',
        }


    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

        if user:
            self.fields['message'].queryset = Message.objects.filter(owner=user)
            self.fields['recipients'].queryset = Recipient.objects.filter(owner=user)
        else:
            self.fields['message'].queryset = Message.objects.all()
            self.fields['recipients'].queryset = Recipient.objects.all()


        if self.instance.pk:
            if self.instance.start_time:
                self.initial['start_time'] = self.instance.start_time.strftime('%Y-%m-%dT%H:%M')
            if self.instance.end_time:
                self.initial['end_time'] = self.instance.end_time.strftime('%Y-%m-%dT%H:%M')
