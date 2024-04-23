from django.core.management.base import BaseCommand
from django.db.models import Prefetch
from api.models import Movie, Genre, Director, Keyword
import csv

class Command(BaseCommand):
    help = 'Exports movie data to a CSV file including director and keyword information'

    def handle(self, *args, **options):
        filename = 'xgboost_enhanced_data.csv'
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['movie_id', 'runtime', 'adult', 'genres', 'directors', 'keywords'])

            # Prefetch related data to minimize database hits
            movies = Movie.objects.all().prefetch_related(
                Prefetch('genres', queryset=Genre.objects.all()),
                Prefetch('directors', queryset=Director.objects.all()),
                Prefetch('keywords', queryset=Keyword.objects.all())
            )

            for movie in movies:
                # Serialize genres, directors, and keywords
                genres = ', '.join(genre.name for genre in movie.genres.all())
                directors = ' '.join(director.name for director in movie.directors.all())
                keywords = ' '.join(keyword.name for keyword in movie.keywords.all())

                # Write to CSV
                writer.writerow([movie.movie_id, movie.runtime, movie.adult, genres, directors, keywords])
        
        self.stdout.write(self.style.SUCCESS(f'Successfully written data to {filename}'))
