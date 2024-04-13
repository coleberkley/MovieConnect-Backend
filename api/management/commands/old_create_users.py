from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from api.models import Movie, Rating
import numpy as np
import random

User = get_user_model()

def generate_custom_rating():
    # Somewhat realistic rating probabilities for a movie
    probabilities = {10: 0.05, 20: 0.1, 30: 0.25, 40: 0.35, 50: 0.25}
    rating = np.random.choice(a=list(probabilities.keys()), p=list(probabilities.values()))
    return rating / 10.0  

class Command(BaseCommand):
    help = 'Populate the database with random user ratings for existing movies'

    def add_arguments(self, parser):
        parser.add_argument('--users', type=int, help='Number of new users to create', default=10)
        parser.add_argument('--ratings_per_user', type=int, help='Number of ratings per user', default=5)

    def handle(self, *args, **options):
        num_users = options['users']
        ratings_per_user = options['ratings_per_user']
        
        # Fetch existing movies from the database
        movie_ids = Movie.objects.values_list('id', flat=True)
        movie_ids = list(movie_ids)
        
        for _ in range(num_users):
            # Create a new user
            new_user = User.objects.create_user(
                username=f'SuperBot_{User.objects.count()+1}',
                email=f'superbot_{User.objects.count()+1}@example.com',
                password='TestPassword123!'  
            )
            
            # Randomly select movies and assign ratings
            rated_movies = random.sample(movie_ids, min(len(movie_ids), ratings_per_user))
            for movie_id in rated_movies:
                Rating.objects.create(
                    user=new_user,
                    movie_id=movie_id,
                    rating=generate_custom_rating()
                )
        
        self.stdout.write(self.style.SUCCESS(f'Successfully created {num_users} users and assigned random ratings.'))
