import csv
from datetime import datetime
from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.db import transaction
from api.models import Movie, Genre, Rating

User = get_user_model()

class Command(BaseCommand):
    help = 'Efficiently import movies, links, and ratings from CSV files'

    def add_arguments(self, parser):
        parser.add_argument('movies_file', type=str)
        parser.add_argument('links_file', type=str)
        parser.add_argument('ratings_file', type=str)

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Starting import process...'))
        # self.import_movies(options['movies_file'])
        # self.update_movies_with_tmdb(options['links_file'])
        # self.import_ratings(options['ratings_file'])
        self.stdout.write(self.style.SUCCESS('Finished importing data.'))

    @transaction.atomic
    def import_movies(self, movies_file):
        genres_dict = {genre.name: genre for genre in Genre.objects.all()}
        movies_list = []
        movie_genres_relations = []

        with open(movies_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                movie = Movie(movie_id=row['movieId'], title=row['title'])
                movies_list.append(movie)
                for genre_name in row['genres'].split('|'):
                    if genre_name not in genres_dict:
                        genre = Genre.objects.create(name=genre_name)
                        genres_dict[genre_name] = genre
                    movie_genres_relations.append((row['movieId'], genre_name))

        Movie.objects.bulk_create(movies_list, ignore_conflicts=True)

        # After movies are created, fetch them to create M2M relations
        movies_dict = {movie.movie_id: movie for movie in Movie.objects.all()}
        for movie_id, genre_name in movie_genres_relations:
            movie = movies_dict[int(movie_id)]
            genre = genres_dict[genre_name]
            movie.genres.add(genre)

    @transaction.atomic
    def update_movies_with_tmdb(self, links_file):
        with open(links_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                tmdb_id_str = row['tmdbId'].strip()
                if tmdb_id_str:  # Check if tmdbId is not an empty string
                    try:
                        tmdb_id = int(tmdb_id_str)
                        Movie.objects.filter(movie_id=row['movieId']).update(tmdb_id=tmdb_id)
                    except ValueError as e:
                        self.stdout.write(self.style.ERROR(f"Invalid tmdbId '{tmdb_id_str}' for movieId {row['movieId']}: {e}"))
                else:
                    self.stdout.write(self.style.WARNING(f"No tmdbId for movieId {row['movieId']}. Skipping."))

    @transaction.atomic
    def import_ratings(self, ratings_file):
        users_dict = {}
        ratings_list = []

        with open(ratings_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                if row['userId'] not in users_dict:
                    # Create a user with a dummy email and default password
                    user, created = User.objects.get_or_create(
                        username=f"user_{row['userId']}",
                        defaults={'email': f"user_{row['userId']}@example.com"}
                    )
                    if created:
                        user.set_password('default_password')
                        user.save()
                    users_dict[row['userId']] = user
                else:
                    user = users_dict[row['userId']]
                movie = Movie.objects.get(movie_id=row['movieId'])
                timestamp = datetime.fromtimestamp(int(row['timestamp']))
                rating_value = int(float(row['rating']))
                ratings_list.append(Rating(user=user, movie=movie, rating=rating_value, timestamp=timestamp))

        Rating.objects.bulk_create(ratings_list, ignore_conflicts=True)

