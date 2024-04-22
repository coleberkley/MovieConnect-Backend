import csv
from django.core.management.base import BaseCommand
from api.models import Movie

class Command(BaseCommand):
    help = 'Load a list of similar movies from a CSV file into the database'

    def handle(self, *args, **options):
        # Path to your CSV file
        path = 'data/similar_movies_data.csv'
        with open(path, mode='r') as csv_file:
            reader = csv.DictReader(csv_file)
            for row in reader:
                # Get the main movie by movie_id
                movie = Movie.objects.filter(movie_id=int(row['movie_id'])).first()
                if movie:
                    similar_movie_ids = [row[f'similar_movie_{i+1}'] for i in range(10) if row[f'similar_movie_{i+1}']]
                    similar_movies = Movie.objects.filter(movie_id__in=similar_movie_ids)
                    movie.similar_movies.set(similar_movies)
                    print(f'Updated {movie.movie_id} with similar movies: {[m.movie_id for m in similar_movies]}')
                else:
                    print(f'Movie with ID {row["movie_id"]} not found')
