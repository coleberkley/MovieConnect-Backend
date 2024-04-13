from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# User model that represents all users of MovieConnect
class GenericUser(AbstractUser):
    # Includes id, username, and password as well
    bio = models.TextField(null=True, blank=True) # Optional bio if we want one
    birth_date = models.DateField(null=True, blank=True) # Expects ISO 8601 format: YYYY-MM-DD
    is_private = models.BooleanField(default=False) # public/private users
    email = models.EmailField(unique=True) # requires unique email for sign-ups
    

class Genre(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Actor(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Director(models.Model):
    name = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.name


class Movie(models.Model):
    title = models.CharField(max_length=255)
    movie_id = models.IntegerField(null=True, unique=True)
    tmdb_id = models.IntegerField(null=True, unique=True)
    genres = models.ManyToManyField(Genre, related_name='movies') 
    poster_url = models.CharField(max_length=255, null=True, blank=True)  # URL to the movie poster
    overview = models.TextField(null=True, blank=True)  # Movie overview or description
    runtime = models.IntegerField(null=True, blank=True)  # Runtime in minutes
    adult = models.BooleanField(default=False) # Indicates if the movie is adult content
    release_date = models.DateField(null=True, blank=True)  # Release date
    keywords = models.TextField(null=True, blank=True)  # Keywords
    actors = models.ManyToManyField(Actor, related_name='movies')
    directors = models.ManyToManyField(Director, related_name='movies')

    def __str__(self):
        return self.title
    

class Rating(models.Model):
    user = models.ForeignKey(GenericUser, on_delete=models.CASCADE, related_name='user_ratings')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='movie_ratings')
    rating = models.FloatField()
    timestamp = models.DateTimeField(auto_now=True)


class WatchedMovie(models.Model):
    user = models.ForeignKey(GenericUser, on_delete=models.CASCADE, related_name='watched_movies')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='watched_by_users')
    watched_on = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'movie')


class FriendRequest(models.Model):
    from_user = models.ForeignKey(GenericUser, on_delete=models.CASCADE, related_name='sent_requests')
    to_user = models.ForeignKey(GenericUser, on_delete=models.CASCADE, related_name='received_requests')
    created_at = models.DateTimeField(default=timezone.now)
    accepted = models.BooleanField(default=False)

    class Meta:
        unique_together = ('from_user', 'to_user')
        

class Comment(models.Model):
    user = models.ForeignKey(GenericUser, on_delete=models.CASCADE, related_name='comments')
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField()
    timestamp = models.DateTimeField(auto_now_add=True)