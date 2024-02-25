from django.core.management.base import BaseCommand
import requests
import json

class Command(BaseCommand):
    help = 'Fetches and prints the JSON response from a TMDB API request'

    def add_arguments(self, parser):
        parser.add_argument('--api_key', type=str, help='Your TMDB API key')

    def handle(self, *args, **options):
        api_key = options['api_key'] if options['api_key'] else '7566a1c11bd5a58fb141c304d73d3c70'
        url = f'https://api.themoviedb.org/3/movie/69?api_key={api_key}'

        response = requests.get(url)
        if response.status_code == 200:
            data = response.json()
            self.stdout.write(json.dumps(data, indent=2))
        else:
            self.stdout.write(self.style.ERROR('Failed to fetch data from TMDB'))
