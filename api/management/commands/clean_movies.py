from django.core.management.base import BaseCommand
from django.db.models import Q
from api.models import Movie, Rating

class Command(BaseCommand):
    help = 'Clean movies and ratings with missing information from the database.'

    def handle(self, *args, **options):
        # Step 1: Identify movies with missing fields
        movies_to_delete = Movie.objects.filter(
            Q(tmdb_id__isnull=True) | 
            Q(poster_url__isnull=True) | 
            Q(poster_url='') | 
            Q(overview__isnull=True) | 
            Q(overview='')
        )
        movie_ids_to_delete = list(movies_to_delete.values_list('movie_id', flat=True))

        # Log the count of movies identified for deletion
        self.stdout.write(self.style.WARNING(f'Identified {len(movie_ids_to_delete)} movies for deletion.'))

        # Step 2: Delete associated ratings
        ratings_deleted_count = Rating.objects.filter(movie_id__in=movie_ids_to_delete).delete()[0]

        # Step 3: Delete the movies
        movies_deleted_count = movies_to_delete.delete()[0]

        # Log the cleanup results
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {movies_deleted_count} movies and {ratings_deleted_count} associated ratings.'))

        # Optional: Write deleted movie IDs to a file
        with open('deleted_movie_ids.txt', 'w') as file:
            for movie_id in movie_ids_to_delete:
                file.write(f'{movie_id}\n')
        self.stdout.write(self.style.SUCCESS(f'Logged deleted movie IDs to deleted_movie_ids.txt.'))
