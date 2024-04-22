from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from api.models import Movie  # Adjust 'your_app' to the actual app name where Movie model is located

User = get_user_model()

class Command(BaseCommand):
    help = 'Prints the watchlist of a specified user'

    def add_arguments(self, parser):
        # Positional argument for username
        parser.add_argument('username', type=str, help='Username of the user whose watchlist is to be printed')

    def handle(self, *args, **options):
        username = options['username']
        try:
            user = User.objects.get(username=username)
            watchlist_movies = user.watchlist.all()
            if watchlist_movies.exists():
                self.stdout.write(self.style.SUCCESS(f"Watchlist for user '{username}':"))
                for movie in watchlist_movies:
                    self.stdout.write(movie.title)
            else:
                self.stdout.write(self.style.WARNING(f"No movies found in the watchlist of user '{username}'."))
        except User.DoesNotExist:
            raise CommandError(f"User '{username}' does not exist")
