from django.core.management.base import BaseCommand, CommandError
from api.models import Movie
import csv

class Command(BaseCommand):
    help = 'Updates movies tmdb_id from a CSV file'

    def add_arguments(self, parser):
        parser.add_argument('csv_file', type=str, help='Path to the CSV file containing movieId and tmdbId')

    def handle(self, *args, **kwargs):

        # This script loops through links.csv and finds the corresponding movie_id in the database
        # to update that movie's tmdb_id field
        # We need to map each movie_id to a tmdb_id for fetching other metadata from TMDb API later


        csv_file_path = kwargs['csv_file']
        updated_count = 0
        not_found_count = 0
        error_count = 0
        duplicate_count = 0

        try:
            with open(csv_file_path, newline='', encoding='utf-8') as csvfile:
                reader = csv.reader(csvfile)
                next(reader)  # Skip the header row
                for row in reader:
                    movie_id, _, tmdb_id_str = row
                    if tmdb_id_str.strip():
                        try:
                            tmdb_id = int(tmdb_id_str)
                            # Check for existing tmdb_id in the database
                            if Movie.objects.filter(tmdb_id=tmdb_id).exists():
                                duplicate_count += 1
                                self.stdout.write(self.style.ERROR(f'Duplicate tmdb_id "{tmdb_id}" found for movie_id {movie_id}. Skipping.'))
                                continue
                            movie = Movie.objects.get(movie_id=movie_id)
                            movie.tmdb_id = tmdb_id
                            movie.save()
                            updated_count += 1
                        except Movie.DoesNotExist:
                            not_found_count += 1
                            self.stdout.write(self.style.WARNING(f'Movie with movie_id {movie_id} not found.'))
                        except ValueError:
                            error_count += 1
                            self.stdout.write(self.style.ERROR(f'Invalid tmdb_id "{tmdb_id_str}" for movie_id {movie_id}.'))
                    else:
                        error_count += 1
                        self.stdout.write(self.style.ERROR(f'Empty tmdb_id for movie_id {movie_id}.'))

        except FileNotFoundError:
            raise CommandError('File "%s" does not exist' % csv_file_path)

        self.stdout.write(self.style.SUCCESS(f'Successfully updated {updated_count} movies.'))
        if not_found_count > 0:
            self.stdout.write(self.style.WARNING(f'{not_found_count} movies not found and were skipped.'))
        if error_count > 0:
            self.stdout.write(self.style.ERROR(f'{error_count} rows had invalid tmdb_id values and were skipped.'))
        if duplicate_count > 0:
            self.stdout.write(self.style.ERROR(f'{duplicate_count} rows had duplicate tmdb_id values and were skipped.'))


