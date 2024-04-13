from django.core.management.base import BaseCommand
from api.models import Movie
import os

class Command(BaseCommand):
    help = 'Log movies with missing actor or director fields to a text file.'

    def handle(self, *args, **options):
        movies = Movie.objects.all()
        missing_info_count = 0

        log_file_path = os.path.join('Logs', 'missing_credits.txt')
        # Open a file to log movies with missing information
        with open(log_file_path, 'w') as log_file:
            for movie in movies:
                missing_fields = []
                if not movie.actors.all().exists():
                    missing_fields.append('actors')
                if not movie.directors.all().exists():
                    missing_fields.append('directors')
                
                if missing_fields:
                    missing_info_count += 1
                    log_message = f'{movie.movie_id}, {movie.title}, Missing fields: {", ".join(missing_fields)}\n'
                    log_file.write(log_message)

            if missing_info_count > 0:
                log_file.write(f'Total movies with missing fields: {missing_info_count}\n')
                self.stdout.write(self.style.WARNING(f'{missing_info_count} movies with missing fields logged to {log_file_path}'))
            else:
                success_message = 'All movies have complete actor and director fields.'
                log_file.write(success_message + '\n')
                self.stdout.write(self.style.SUCCESS(success_message))
