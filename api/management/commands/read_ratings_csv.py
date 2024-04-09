from django.core.management.base import BaseCommand, CommandError
from django.contrib.auth import get_user_model
from api.models import Movie, Rating
import csv
from datetime import datetime
import pytz

User = get_user_model()

class Command(BaseCommand):
    help = 'Import users and their ratings from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing the ratings')

    def handle(self, *args, **kwargs):
        csv_file_path = kwargs['csv_file']
        users_created = 0
        ratings_created = 0

        try:
            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                for row in reader:
                    userId = row['userId']
                    username = f'user{userId}'
                    # Check if user exists, otherwise create a new one
                    user, created = User.objects.get_or_create(
                        username=username,
                        defaults={
                            'email': f'{username}@example.com',
                            'password': 'genericpassword123'  # Consider using a more secure password or prompt users to change it
                        }
                    )
                    if created:
                        users_created += 1
                    
                    movieId = row['movieId']
                    rating = row['rating']
                    timestamp = row['timestamp']
                    rating_datetime = datetime.utcfromtimestamp(int(timestamp)).replace(tzinfo=pytz.UTC)


                    # Ensure the movie exists before creating the rating
                    if Movie.objects.filter(movie_id=movieId).exists():
                        movie = Movie.objects.get(movie_id=movieId)
                        Rating.objects.create(
                            user=user,
                            movie=movie,
                            rating=rating,
                            timestamp=rating_datetime  
                        )
                        ratings_created += 1
                    else:
                        self.stdout.write(self.style.WARNING(f'Movie with movie_id {movieId} not found.'))

        except FileNotFoundError:
            raise CommandError(f'File "{csv_file_path}" does not exist')

        self.stdout.write(self.style.SUCCESS(f'Successfully created {users_created} users and {ratings_created} ratings.'))
