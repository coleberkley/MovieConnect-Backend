from django.core.management.base import BaseCommand
from django.db.models import Avg
from api.models import Movie, Rating

class Command(BaseCommand):
    help = 'Calculates average ratings for each movie and updates the database'

    def handle(self, *args, **options):
        for movie in Movie.objects.all():
            average = movie.movie_ratings.aggregate(avg_rating=Avg('rating'))['avg_rating']
            movie.avg_rating = average
            movie.save()
            self.stdout.write(self.style.SUCCESS(f'Successfully updated avg_rating for {movie.title} as {average}'))
