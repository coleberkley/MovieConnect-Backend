from django.contrib import admin
from .models import GenericUser, Person, Keyword, Genre, Movie, MovieKeyword, MoviePerson, Rating, WatchedMovie

# Register your models here.
admin.site.register(GenericUser)
admin.site.register(Person)
admin.site.register(Keyword)
admin.site.register(Genre)
admin.site.register(Movie)
admin.site.register(MovieKeyword)
admin.site.register(MoviePerson)
admin.site.register(Rating)
admin.site.register(WatchedMovie)
