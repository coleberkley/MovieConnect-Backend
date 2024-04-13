from django.core.management.base import BaseCommand
from api.models import Movie
import os

class Command(BaseCommand):
    help = 'Log movies missing tmdb_id to a text file in the Logs directory.'

    def handle(self, *args, **options):
        log_file_path = os.path.join('Logs', 'missing_tmdb.txt')

        movies_missing_tmdb_id = Movie.objects.filter(tmdb_id__isnull=True)
        count = movies_missing_tmdb_id.count()

        # Always open the file to write the log
        with open(log_file_path, 'w') as log_file:
            if count > 0:
                for movie in movies_missing_tmdb_id:
                    log_message = f'{movie.movie_id}, {movie.title}\n'
                    log_file.write(log_message)
                self.stdout.write(self.style.WARNING(f'{count} movies missing tmdb_id logged to {log_file_path}'))
            else:
                success_message = 'No movies are missing tmdb_id.'
                log_file.write(success_message + '\n')
                self.stdout.write(self.style.SUCCESS(success_message))


