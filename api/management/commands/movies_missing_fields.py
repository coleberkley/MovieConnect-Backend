    # Skip movies that already have poster_url, overview, runtime, and adult fields filled
from django.core.management.base import BaseCommand
from api.models import Movie

class Command(BaseCommand):
    help = 'Log movies with missing specified fields to a text file.'

    def handle(self, *args, **options):
        movies = Movie.objects.all()
        missing_info_count = 0

        # Open a file to log movies with missing information
        with open('movies_missing_fields.txt', 'w') as log_file:
            for movie in movies:
                missing_fields = []
                # if not movie.tmdb_id:
                #     missing_fields.append('tmdb_id')
                # if movie.runtime is None:
                #     missing_fields.append('runtime')
                if not movie.poster_url:
                    missing_fields.append('poster_url')
                # if movie.adult is None:
                #     missing_fields.append('adult')
                if not movie.overview:
                    missing_fields.append('overview')
                
                if missing_fields:
                    missing_info_count += 1
                    log_message = f'{movie.movie_id}, {movie.title}, Missing fields: {", ".join(missing_fields)}\n'
                    log_file.write(log_message)

        if missing_info_count > 0:
            self.stdout.write(self.style.WARNING(f'{missing_info_count} movies with missing fields logged to movies_missing_fields.txt'))
        else:
            self.stdout.write(self.style.SUCCESS('All movies have complete fields.'))
