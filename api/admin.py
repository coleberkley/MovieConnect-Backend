from django.contrib import admin
from .models import GenericUser, Genre, Movie, Rating, WatchedMovie, Comment, FriendRequest, Actor, Director, Keyword

# Register your models here.
admin.site.register(GenericUser)
admin.site.register(Genre)
admin.site.register(Actor)
admin.site.register(Director)
admin.site.register(Movie)
admin.site.register(Rating)
admin.site.register(WatchedMovie)
admin.site.register(Comment)
admin.site.register(FriendRequest)
admin.site.register(Keyword)

