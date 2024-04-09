from django.core.management.base import BaseCommand
from api.models import Movie
import requests
import os
import time

class Command(BaseCommand):
    help = 'Update movies with poster URL, overview, and runtime from TMDb API'

    def handle(self, *args, **options):
        api_key = os.getenv('TMDB_KEY')
        if not api_key:
            self.stdout.write(self.style.ERROR('TMDB_KEY environment variable not found.'))
            return

        movies = Movie.objects.all()
        total_movies = movies.count()
        self.stdout.write(f'Starting to update {total_movies} movies...')

        success_count = 0
        fail_count = 0

        # Open a file to log failed TMDB IDs
        with open('failed_tmdb_ids.txt', 'w') as log_file:

            for movie in movies:
                # Skip movies that already have poster_url, overview, runtime, and adult fields filled
                if movie.poster_url and movie.overview and movie.runtime is not None and movie.adult is not None:
                    self.stdout.write(self.style.SUCCESS(f'Skipping {movie.title} as it already has all fields filled.'))
                    continue

                # Print tmdb_id before attempting the request
                self.stdout.write(f'Processing {movie.title} with tmdb_id: {movie.tmdb_id}')

                # Skip movies without a valid tmdb_id
                if not movie.tmdb_id:
                    self.stdout.write(self.style.WARNING(f'Skipping {movie.title} due to missing tmdb_id'))
                    fail_count += 1
                    continue

                # Handle rate limiting
                time.sleep(0.1)  # Adjust based on the actual rate limit you wish to maintain

                retry_count = 0
                max_retries = 3  # Maximum number of retries per movie
                while retry_count < max_retries:
                    try:
                        response = requests.get(f'https://api.themoviedb.org/3/movie/{movie.tmdb_id}?api_key={api_key}')

                        # Check if request was successful
                        if response.status_code == 200:
                            data = response.json()
                            movie.poster_url = f"https://image.tmdb.org/t/p/original{data.get('poster_path')}"
                            movie.overview = data.get('overview')
                            movie.runtime = data.get('runtime')
                            movie.adult = data.get('adult', False)  # Set the adult field, default to False if not provided
                            movie.save()
                            success_count += 1
                            self.stdout.write(self.style.SUCCESS(f'Successfully updated {movie.title}'))
                            break  # Exit retry loop on success
                        else:
                            # Log failed requests to debug or handle accordingly
                            self.stdout.write(self.style.WARNING(f'Failed request for {movie.title} with tmdb_id: {movie.tmdb_id}, retrying...'))
                            retry_count += 1
                            time.sleep(1)  # Wait a bit longer before retrying
                    except Exception as e:
                        self.stdout.write(self.style.ERROR(f'Error updating {movie.title}: {str(e)}'))
                        fail_count += 1
                        break  # Exit retry loop on exception

                # After max retries, log the TMDB ID to file
                if retry_count >= max_retries:
                    log_message = f'Failed to update {movie.title} with TMDB ID: {movie.tmdb_id}\n'
                    log_file.write(log_message)
                    self.stdout.write(self.style.ERROR(log_message))

        self.stdout.write(self.style.SUCCESS(f'Update completed. {success_count} movies updated successfully.'))
        if fail_count > 0:
            self.stdout.write(self.style.WARNING(f'{fail_count} movies failed to update. Check failed_tmdb_ids.txt for details.'))


