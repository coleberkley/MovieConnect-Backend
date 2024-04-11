from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Movie, Genre, Rating, Comment, FriendRequest
from django.db.models import Avg
from django.utils import timezone
from rest_framework.validators import UniqueValidator

# Gets current User model declared in settings.py
User = get_user_model()

class GenericUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username']


class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'birth_date', 'is_private', 'bio']


# Serializer for user sign up
class UserSignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    birth_date = serializers.DateField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'birth_date']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            birth_date=validated_data['birth_date']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user


# Serializer for updating user profile
class UpdateProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'is_private']
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'username': {'required': False},
            'email': {'required': False},
            'is_private': {'required': False},
        }

    def update(self, instance, validated_data):
        # Update the username, email, and is_private status if provided
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.is_private = validated_data.get('is_private', instance.is_private)
        
        # Handle password update securely
        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)
        
        instance.save()
        return instance


# Serializer for displaying each movie in a movie list
class DisplayMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['id', 'title', 'poster_url', 'overview', 'release_date', 'runtime', 'adult']


# Serializer for a genre
class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ['name']


class CommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = ['id', 'body', 'timestamp', 'username']


# Serializer for displaying the detailed view of a movie for a movie page
class MovieDetailSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    rated = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ['id', 'title', 'poster_url', 'overview', 'runtime', 'adult', 'cast', 'release_date', 'genres', 'average_rating', 'rated']

    def get_average_rating(self, obj):
        ratings = Rating.objects.filter(movie=obj)
        if ratings.exists():
            average = ratings.aggregate(Avg('rating'))['rating__avg']
            return round(average, 1)
        return 0

    def get_rated(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return 0
        rating = Rating.objects.filter(user=user, movie=obj).first()
        return rating.rating if rating else 0


# Serializer for adding or updating a rating
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['movie', 'user', 'rating']
        extra_kwargs = {
            'user': {'read_only': True},
            'movie': {'read_only': True}
        }

    def create(self, validated_data):
        # Creating a new rating
        user = self.context['request'].user
        movie_id = self.context['view'].kwargs['pk']
        rating = validated_data['rating']
        return Rating.objects.create(user=user, movie_id=movie_id, rating=rating)

    def update(self, instance, validated_data):
        # Updating an existing rating
        instance.rating = validated_data.get('rating', instance.rating)
        instance.save()
        return instance


class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    to_user = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'created_at', 'accepted']
