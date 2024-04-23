from django.core.management.base import BaseCommand
from api.models import Movie
import csv

class Command(BaseCommand):
    help = 'Exports movie data to a CSV file'

    def handle(self, *args, **options):
        filename = 'xgboost_static_data.csv'
        with open(filename, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['movie_id', 'genres', 'runtime', 'adult'])
            for movie in Movie.objects.all().prefetch_related('genres'):
                genres = ', '.join(genre.name for genre in movie.genres.all())
                writer.writerow([movie.movie_id, genres, movie.runtime, movie.adult])
        
        self.stdout.write(self.style.SUCCESS(f'Successfully written data to {filename}'))
