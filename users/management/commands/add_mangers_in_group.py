from django.contrib.auth.models import Group
from django.core.management.base import BaseCommand


from users.models import CustomUser


class Command(BaseCommand):
    help = "Добавляет пользователей в группы Менеджеры."

    def handle(self, *args, **options):
        group_name = "Менеджеры"
        self.stdout.write(f'Поиск или создание группы "{group_name}"...')

        managers_group, created = Group.objects.get_or_create(name=group_name)

        if created:
            self.stdout.write(self.style.SUCCESS(f'Группа "{group_name}" успешно создана.'))
        else:
            self.stdout.write(self.style.WARNING(f'Группа "{group_name}" уже существует.'))

        users_to_add = ["admin@example.com", "tkuleva@geely_iat.ru"]
        added_count = 0

        for username in users_to_add:
            user, user_created = CustomUser.objects.get_or_create(email=username)
            if user_created:
                user.set_password("defaultpassword123")
                user.save()
                self.stdout.write(f'Пользователь "{username}" создан.')

            if not user.groups.filter(name=group_name).exists():
                managers_group.user_set.add(user)
                self.stdout.write(f'Пользователь "{username}" добавлен в группу "{group_name}".')
                added_count += 1
            else:
                self.stdout.write(f'Пользователь "{username}" уже в группе "{group_name}".')

        if added_count > 0:
            self.stdout.write(
                self.style.SUCCESS(f'Всего добавлено {added_count} новых пользователей в группу "{group_name}".')
            )
        else:
            self.stdout.write(self.style.WARNING("Новых пользователей не добавлено."))
