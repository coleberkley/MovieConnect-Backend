from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

class Command(BaseCommand):
    help = 'Deletes all User instances from the database'

    def handle(self, *args, **options):
        UserModel = get_user_model()
        UserModel.objects.all().delete()
        self.stdout.write(self.style.SUCCESS('Successfully deleted all GenericUser instances'))
