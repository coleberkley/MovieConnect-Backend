from django.core.management.base import BaseCommand
from api.models import Movie, Actor, Director
import requests
import os
import time

class Command(BaseCommand):
    help = 'Populate database with actor and director data from TMDb API'

    def handle(self, *args, **options):
        api_key = os.getenv('TMDB_KEY')
        if not api_key:
            self.stdout.write(self.style.ERROR('TMDB_KEY environment variable not found.'))
            return

        movies = Movie.objects.all()
        total_movies = movies.count()
        self.stdout.write(f'Starting to populate actor and director data for {total_movies} movies...')

        success_count = 0
        skipped_count = 0

        for movie in movies:
            self.stdout.write(f'Processing {movie.title} with tmdb_id: {movie.tmdb_id}')
            if not movie.tmdb_id:
                self.stdout.write(self.style.WARNING(f'Skipping {movie.title} due to missing tmdb_id'))
                skipped_count += 1
                continue

            # Check if movie already has actors or directors populated
            if movie.actors.exists() or movie.directors.exists():
                self.stdout.write(self.style.NOTICE(f'Skipping {movie.title} as it already has actor/director data.'))
                skipped_count += 1
                continue

            # Handle rate limiting
            time.sleep(0.1)
            retry_count = 0
            max_retries = 5

            while retry_count < max_retries:
                try:
                    credits_response = requests.get(
                        f'https://api.themoviedb.org/3/movie/{movie.tmdb_id}/credits?api_key={api_key}'
                    )
                    if credits_response.status_code == 200:
                        credits_data = credits_response.json()
                        actors_data = credits_data.get('cast', [])
                        directors_data = [crew for crew in credits_data.get('crew', []) if crew['job'] == 'Director']

                        # Process actors
                        for actor_info in actors_data:
                            actor, created = Actor.objects.get_or_create(name=actor_info['name'])
                            movie.actors.add(actor)

                        # Process directors
                        for director_info in directors_data:
                            director, created = Director.objects.get_or_create(name=director_info['name'])
                            movie.directors.add(director)

                        movie.save()
                        success_count += 1
                        self.stdout.write(self.style.SUCCESS(f'Successfully populated {movie.title}'))
                        break
                    else:
                        self.stdout.write(self.style.WARNING(f'Failed to fetch credits for {movie.title}, retrying...'))
                        retry_count += 1
                        time.sleep(0.5)  # Wait before retrying
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f'Error processing {movie.title}: {str(e)}'))
                    retry_count += 1
                    time.sleep(1)
                    # break  # Stop retrying after an exception

        self.stdout.write(self.style.SUCCESS(f'Population completed. {success_count} movies updated successfully.'))
        self.stdout.write(self.style.NOTICE(f'{skipped_count} movies were skipped because they already had data.'))




