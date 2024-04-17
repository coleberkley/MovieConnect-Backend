from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

User = get_user_model()

class Command(BaseCommand):
    help = 'Update passwords for users with usernames starting with "user"'

    def add_arguments(self, parser):
        parser.add_argument('--password', type=str, help='New password for selected users', default='password123')

    def handle(self, *args, **kwargs):
        new_password = kwargs['password']
        users_updated = 0

        # Filter users whose username starts with 'user'
        users_to_update = User.objects.filter(username__startswith='user')
        
        for user in users_to_update:
            user.set_password(new_password)
            user.save()
            users_updated += 1
            self.stdout.write(self.style.SUCCESS(f'Updated password for {user.username}'))

        self.stdout.write(self.style.SUCCESS(f'Successfully updated passwords for {users_updated} users.'))
