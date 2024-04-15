from django.core.management.base import BaseCommand
from api.models import Movie, Keyword
import requests
import os
import time

class Command(BaseCommand):
    help = 'Populate database with keyword data from TMDb API'

    def handle(self, *args, **options):
        api_key = os.getenv('TMDB_KEY')
        if not api_key:
            self.stdout.write(self.style.ERROR('TMDB_KEY environment variable not found.'))
            return

        movies = Movie.objects.all()
        total_movies = movies.count()
        self.stdout.write(f'Starting to populate keyword data for {total_movies} movies...')

        success_count = 0
        skipped_count = 0

        for movie in movies:
            self.stdout.write(f'Processing {movie.title} with tmdb_id: {movie.tmdb_id}')
            if not movie.tmdb_id:
                self.stdout.write(self.style.WARNING(f'Skipping {movie.title} due to missing tmdb_id'))
                skipped_count += 1
                continue

            # Correct check for existing keywords
            if movie.keywords.count() > 0:
                self.stdout.write(self.style.NOTICE(f'Skipping {movie.title} as it already has keyword data.'))
                skipped_count += 1
                continue

            time.sleep(0.1)  # Handle rate limiting
            retry_count = 0
            max_retries = 5

            while retry_count < max_retries:
                try:
                    keywords_response = requests.get(
                        f'https://api.themoviedb.org/3/movie/{movie.tmdb_id}/keywords?api_key={api_key}'
                    )
                    if keywords_response.status_code == 200:
                        keywords_data = keywords_response.json().get('keywords', [])
                        
                        for keyword_info in keywords_data:
                            keyword, created = Keyword.objects.get_or_create(name=keyword_info['name'])
                            movie.keywords.add(keyword)

                        movie.save()
                        success_count += 1
                        self.stdout.write(self.style.SUCCESS(f'Successfully populated {movie.title}'))
                        break
                    else:
                        self.stdout.write(self.style.WARNING(f'Failed to fetch keywords for {movie.title}, retrying...'))
                        retry_count += 1
                        time.sleep(0.5)  # Wait before retrying
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing {movie.title}: {str(e)}'))
                    retry_count += 1
                    time.sleep(1)

        self.stdout.write(self.style.SUCCESS(f'Population completed. {success_count} movies updated successfully.'))
        self.stdout.write(self.style.NOTICE(f'{skipped_count} movies were skipped.'))



