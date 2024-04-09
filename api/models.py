from django.contrib.auth.models import AbstractUser
from django.db import models

# User model that represents all users of MovieConnect
class GenericUser(AbstractUser):
    # Includes id, username, and password as well
    bio = models.TextField(null=True, blank=True) # Optional bio if we want one
    birth_date = models.DateField(null=True, blank=True) # Expects ISO 8601 format: YYYY-MM-DD
    is_private = models.BooleanField(default=False) # public/private users
    email = models.EmailField(unique=True) # requires unique email for sign-ups


# class Person(models.Model):
#     name = models.CharField(max_length=255) 
#     birth_date = models.DateField(null=True, blank=True)
#     gender = models.IntegerField(null=True, blank=True)  # 0 = not known, 1 = female, 2 = male


# class Keyword(models.Model):
#     name = models.CharField(max_length=255, unique=True)

#     def __str__(self):
#         return self.name
    

class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name
    
    
class Movie(models.Model):
    title = models.CharField(max_length=255)
    movie_id = models.IntegerField(null=True, unique=True)
    tmdb_id = models.IntegerField(null=True, unique=True)
    genres = models.ManyToManyField(Genre, related_name='movies') 
    # keywords = models.ManyToManyField(Keyword, through='MovieKeyword', related_name='movies') 
    # ratings = models.ManyToManyField(GenericUser, through='Rating', related_name='rated_movies')
    # people = models.ManyToManyField(Person, through='MoviePerson', related_name='movies')
    poster_url = models.CharField(max_length=255, null=True, blank=True)  # URL to the movie poster
    overview = models.TextField(null=True, blank=True)  # Movie overview or description
    runtime = models.IntegerField(null=True, blank=True)  # Runtime in minutes
    adult = models.BooleanField(default=False) # Indicates if the movie is adult content

    def __str__(self):
        return self.title
    

# class MovieKeyword(models.Model):
#     movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
#     keyword = models.ForeignKey(Keyword, on_delete=models.CASCADE)

#     class Meta:
#         unique_together = ('movie', 'keyword')


# class MoviePerson(models.Model):
#     movie = models.ForeignKey(Movie, on_delete=models.CASCADE)
#     person = models.ForeignKey(Person, on_delete=models.CASCADE)
#     role = models.CharField(max_length=255)  # E.g., "Actor", "Director"
#     character_name = models.CharField(max_length=255, null=True, blank=True)  # Only relevant for actors


class Rating(models.Model):
    user = models.ForeignKey(GenericUser, on_delete=models.CASCADE, related_name='user_ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_ratings')
    rating = models.FloatField()
    timestamp = models.DateTimeField()


class WatchedMovie(models.Model):
    user = models.ForeignKey(GenericUser, on_delete=models.CASCADE, related_name='watched_movies')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watched_by_users')
    watched_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')
