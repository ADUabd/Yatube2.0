from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from apps.users.models import Profile

User = get_user_model()


class Command(BaseCommand):
    help = 'Создает профили для всех пользователей, у которых их нет'

    def handle(self, *args, **options):
        users_without_profile = User.objects.filter(profile__isnull=True)
        count = 0
        
        for user in users_without_profile:
            Profile.objects.create(user=user)
            count += 1
            self.stdout.write(f'Создан профиль для: {user.username}')
        
        if count:
            self.stdout.write(
                self.style.SUCCESS(f'Успешно создано {count} профилей.')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS('Все пользователи уже имеют профили.')
            )
