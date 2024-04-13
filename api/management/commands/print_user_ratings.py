from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import Rating

User = get_user_model()

class Command(BaseCommand):
    help = 'List all rated movies for a specific user.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username of the user.')

    def handle(self, *args, **options):
        username = options['username']

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(self.style.ERROR(f'User "{username}" does not exist.'))
            return
        
        # Fetch rated movies and their ratings for the user
        rated_movies = Rating.objects.filter(user=user).select_related('movie').order_by('-timestamp')

        if rated_movies:
            self.stdout.write(self.style.SUCCESS(f'Rated movies for {username}:'))
            for rating in rated_movies:
                movie = rating.movie
                self.stdout.write(f'{movie.title} - Rating: {rating.rating}')
        else:
            self.stdout.write(self.style.WARNING(f'No rated movies found for {username}.'))
