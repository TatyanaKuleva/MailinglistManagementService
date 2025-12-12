from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


class Command(BaseCommand):
    help = "Создает 2 группы: Пользователь и Менеджер с разрешениями"

    def handle(self, *args, **kwargs):
        user_group, created = Group.objects.get_or_create(name="Пользователь")
        manager_group, created = Group.objects.get_or_create(name="Менеджер")

        self.stdout.write(self.style.SUCCESS("Группы созданы/обновлены"))
