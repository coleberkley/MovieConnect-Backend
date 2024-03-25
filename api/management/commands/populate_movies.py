import requests
from django.core.management.base import BaseCommand
from django.db import transaction
from api.models import Movie, Genre, Person, MovieKeyword, Keyword, MoviePerson
import os

class Command(BaseCommand):
    help = 'Populates the database with movies from TMDb'

    def handle(self, *args, **options):
        tmdb_api_key = os.getenv('TMDB_KEY')
        popular_movies_url = f'https://api.themoviedb.org/3/movie/popular?api_key={tmdb_api_key}&language=en-US&page='

        for page in range(12, 16):  # Fetch 1 page of popular movies, last page fetched from TMDb was 15
            response = requests.get(popular_movies_url + str(page)).json()
            for movie_data in response['results']:
                # Fetch additional movie details
                details_url = f'https://api.themoviedb.org/3/movie/{movie_data["id"]}?api_key={tmdb_api_key}&language=en-US'
                details_response = requests.get(details_url).json()

                # Fetch movie credits
                credits_url = f'https://api.themoviedb.org/3/movie/{movie_data["id"]}/credits?api_key={tmdb_api_key}&language=en-US'
                credits_response = requests.get(credits_url).json()

                # Fetch movie keywords
                keywords_url = f'https://api.themoviedb.org/3/movie/{movie_data["id"]}/keywords?api_key={tmdb_api_key}'
                keywords_response = requests.get(keywords_url).json()

                with transaction.atomic():
                    # Create or update the movie instance
                    movie, created = Movie.objects.update_or_create(
                        tmdb_id=movie_data['id'],
                        defaults={
                            'title': movie_data['title'],
                            'poster_path': movie_data.get('poster_path', ''),
                            'overview': movie_data['overview'],
                            'release_date': movie_data['release_date'],
                            'runtime': details_response.get('runtime', 0),
                            'language': details_response.get('original_language', ''),
                            'adult': movie_data['adult'],
                        }
                    )

                    # Add genres
                    for genre_data in details_response['genres']:
                        genre, _ = Genre.objects.get_or_create(name=genre_data['name'])
                        movie.genres.add(genre)

                    # Add keywords
                    for keyword_data in keywords_response['keywords']:
                        keyword, _ = Keyword.objects.get_or_create(name=keyword_data['name'])
                        # Ensure the keyword is associated with the movie
                        MovieKeyword.objects.get_or_create(movie=movie, keyword=keyword)

                    # Add people (cast and crew)
                    for cast_member in credits_response['cast']:
                        person, _ = Person.objects.get_or_create(
                            name=cast_member['name'],
                            defaults={'gender': cast_member['gender']}
                        )
                        MoviePerson.objects.get_or_create(movie=movie, person=person, role='Actor', character_name=cast_member.get('character', ''))

                    for crew_member in credits_response['crew']:
                        person, _ = Person.objects.get_or_create(
                            name=crew_member['name'],
                            defaults={'gender': crew_member['gender']}
                        )
                        MoviePerson.objects.get_or_create(movie=movie, person=person, role=crew_member['job'])

        self.stdout.write(self.style.SUCCESS('Successfully populated movies from TMDb.'))
