# api/management/commands/export_movie_data.py

from django.core.management.base import BaseCommand
from api.models import Movie, Genre, Actor, Director, Keyword, Rating
import pandas as pd

class Command(BaseCommand):
    help = 'Export movie and rating data to CSV for machine learning purposes'

    def handle(self, *args, **options):
        # Export Movies with Metadata
        movies = Movie.objects.prefetch_related('genres', 'keywords', 'actors', 'directors').all()
        movie_data = []
        for movie in movies:
            movie_data.append({
                "movie_id": movie.movie_id,
                "title": movie.title,
                "genres": ', '.join([genre.name for genre in movie.genres.all()]),
                "keywords": ', '.join([keyword.name for keyword in movie.keywords.all()]),
                "actors": ', '.join([actor.name for actor in movie.actors.all()]),
                "directors": ', '.join([director.name for director in movie.directors.all()]),
                "overview": movie.overview,
                "runtime": movie.runtime,
                "adult": movie.adult,
                "release_date": movie.release_date
            })
        movie_df = pd.DataFrame(movie_data)
        movie_df.to_csv('db_movies_metadata.csv', index=False)
        self.stdout.write(self.style.SUCCESS('Successfully exported movie metadata to movies_metadata.csv'))

        ratings = Rating.objects.select_related('user', 'movie').all()
        ratings_data = [{
            "user_id": rating.user.id,
            "username": rating.user.username,
            "movie_id": rating.movie.movie_id,
            "rating": rating.rating,
            "timestamp": rating.timestamp
        } for rating in ratings]
        ratings_df = pd.DataFrame(ratings_data)
        ratings_df.to_csv('db_ratings.csv', index=False)
        self.stdout.write(self.style.SUCCESS('Successfully exported ratings to ratings.csv'))
