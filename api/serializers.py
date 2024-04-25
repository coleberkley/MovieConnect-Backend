from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Movie, Genre, Rating, Comment, FriendRequest, Actor, Director
from django.db.models import Avg
from django.utils import timezone
from rest_framework.validators import UniqueValidator
from django.db.models import Q


# Gets current User model declared in settings.py
User = get_user_model()

# Old Unused Serializer
class GenericUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


# Old Unused Serializer
class UserNameSerializer(serializers.ModelSerializer):
    class Meta:
        model = get_user_model()
        fields = ['username']


# Serializer for user id and username fields
class UserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username']


# Serializer for User Profile fields
class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'birth_date', 'is_private', 'bio']


# Serializer for a different User Profile's fields
class OtherUserProfileSerializer(serializers.ModelSerializer):
    is_friend = serializers.SerializerMethodField()
    is_outgoing = serializers.SerializerMethodField()
    is_incoming = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ['id', 'username', 'bio', 'is_private', 'is_friend', 'is_outgoing', 'is_incoming']

    def get_is_friend(self, obj):
        request_user = self.context['request'].user
        friend_request = FriendRequest.objects.filter(
            Q(from_user=request_user, to_user=obj, accepted=True) |
            Q(from_user=obj, to_user=request_user, accepted=True)
        ).first()
        return friend_request.id if friend_request else None

    def get_is_outgoing(self, obj):
        request_user = self.context['request'].user
        friend_request = FriendRequest.objects.filter(
            from_user=request_user, 
            to_user=obj, 
            accepted=False
        ).first()
        return friend_request.id if friend_request else None

    def get_is_incoming(self, obj):
        request_user = self.context['request'].user
        friend_request = FriendRequest.objects.filter(
            from_user=obj, 
            to_user=request_user, 
            accepted=False
        ).first()
        return friend_request.id if friend_request else None


# Serializer for user sign up
class UserSignUpSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(
        required=True,
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    username = serializers.CharField(
        validators=[UniqueValidator(queryset=User.objects.all())]
    )
    # password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    password = serializers.CharField(write_only=True, required=True)
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
        fields = ['username', 'email', 'password', 'is_private', 'bio'] 
        extra_kwargs = {
            'password': {'write_only': True, 'required': False},
            'username': {'required': False},
            'email': {'required': False},
            'is_private': {'required': False},
            'bio': {'required': False}  
        }

    def update(self, instance, validated_data):
        # Update the username, email, is_private status, and bio if provided
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.is_private = validated_data.get('is_private', instance.is_private)
        instance.bio = validated_data.get('bio', instance.bio)  # Update bio

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


# Serializer for an actor
class ActorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Actor
        fields = ['name']


# Serializer for a director
class DirectorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Director
        fields = ['name']


# Serializer for a comment
class CommentSerializer(serializers.ModelSerializer):
    username = serializers.ReadOnlyField(source='user.username')

    class Meta:
        model = Comment
        fields = ['id', 'body', 'timestamp', 'username']


# Serializer for displaying the detailed view of a movie for a movie page
class MovieDetailSerializer(serializers.ModelSerializer):
    genres = GenreSerializer(many=True, read_only=True)
    actors = ActorSerializer(many=True, read_only=True)
    directors = DirectorSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    rated = serializers.SerializerMethodField()
    on_watchlist = serializers.SerializerMethodField() 


    class Meta:
        model = Movie
        fields = [
            'id', 'title', 'poster_url', 'overview', 'runtime', 'adult',
            'release_date', 'genres', 'actors', 'directors', 'average_rating', 'rated', 'on_watchlist'
        ]

    def get_average_rating(self, obj):
        # Return avg_rating rounded to 1 decimal place, or None if it's null
        return round(obj.avg_rating, 1) if obj.avg_rating is not None else None

    def get_rated(self, obj):
        user = self.context['request'].user
        if not user.is_authenticated:
            return 0
        rating = Rating.objects.filter(user=user, movie=obj).first()
        return rating.rating if rating else 0
    
    def get_on_watchlist(self, obj):
        user = self.context['request'].user
        return obj.watchlisted_by.filter(id=user.id).exists()


# Serializer for another user's rated movie list
class UserRatedMoviesSerializer(serializers.ModelSerializer):
    user_rating = serializers.SerializerMethodField()

    class Meta:
        model = Movie
        fields = ['id', 'title', 'poster_url', 'overview', 'release_date', 'runtime', 'adult', 'user_rating']

    def get_user_rating(self, obj):
        user = self.context.get('user')
        rating = Rating.objects.filter(user=user, movie=obj).first()
        return rating.rating if rating else None



# Serializer for adding or updating a rating
class RatingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rating
        fields = ['id', 'movie', 'user', 'rating', 'timestamp']
        read_only_fields = ['id', 'user', 'movie', 'timestamp']  # Ensures these fields are not writable directly

    # No need for custom create or update methods if they're handled in the view


# Serializer for friend requests
class FriendRequestSerializer(serializers.ModelSerializer):
    from_user = serializers.SlugRelatedField(slug_field='username', read_only=True)
    to_user = serializers.SlugRelatedField(slug_field='username', read_only=True)

    class Meta:
        model = FriendRequest
        fields = ['id', 'from_user', 'to_user', 'created_at', 'accepted']