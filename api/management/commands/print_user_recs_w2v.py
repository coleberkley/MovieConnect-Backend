from django.core.management.base import BaseCommand
from api.algorithms.xgboost_w2v_opt import recommend_movies

class Command(BaseCommand):
    help = 'Generate movie recommendations for a specified user.'

    def add_arguments(self, parser):
        parser.add_argument('username', type=str, help='The username of the user to generate recommendations for.')

    def handle(self, *args, **options):
        username = options['username']

        recommendations = recommend_movies(username)
        if recommendations:
            self.stdout.write(self.style.SUCCESS(f"Recommendations for {username}:"))
            for movie_title in recommendations:
                self.stdout.write(movie_title)
        else:
            self.stdout.write(self.style.WARNING(f'No recommendations available for {username}.'))