from django.core.management.base import BaseCommand
from api.models import Movie

class Command(BaseCommand):
    help = 'Log movies missing tmdb_id to a text file.'

    def handle(self, *args, **options):
        movies_missing_tmdb_id = Movie.objects.filter(tmdb_id__isnull=True)
        count = movies_missing_tmdb_id.count()

        if count > 0:
            with open('movies_missing_tmdb_id.txt', 'w') as log_file:
                for movie in movies_missing_tmdb_id:
                    log_message = f'{movie.movie_id}, {movie.title}\n'
                    log_file.write(log_message)

            self.stdout.write(self.style.WARNING(f'{count} movies missing tmdb_id logged to movies_missing_tmdb_id.txt'))
        else:
            self.stdout.write(self.style.SUCCESS('No movies are missing tmdb_id.'))
