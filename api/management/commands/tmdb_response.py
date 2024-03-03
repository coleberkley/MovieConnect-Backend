from django.core.management.base import BaseCommand
import requests
import json
import os

# Some routes for testing:

# Get the top rated movies:
# https://api.themoviedb.org/3/movie/top_rated?api_key={api_key}

# Get popular movies:
# https://api.themoviedb.org/3/movie/popular?api_key={api_key}

# Get a movie's details by ID:
# https://api.themoviedb.org/3/movie/{movie_id}?api_key={api_key}

# Get a movie credit details by ID: (Actors and Directors)
# https://api.themoviedb.org/3/movie/{movie_id}/credits?api_key={api_key}

# Get a movie's keywords by ID:
# https://api.themoviedb.org/3/movie/{movie_id}/keywords?api_key={api_key}

# Append '&page={number}' at the end to set page number


class Command(BaseCommand):

    def handle(self, *args, **options):
        movie_id = 69
        api_key = os.getenv('TMDB_KEY')
        url = f'https://api.themoviedb.org/3/movie/{movie_id}/keywords?api_key={api_key}'

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            self.stdout.write(json.dumps(data, indent=2))
        else:
            self.stdout.write(self.style.ERROR('Failed to fetch data from TMDB'))
