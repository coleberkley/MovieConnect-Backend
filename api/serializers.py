from django.contrib.auth import get_user_model
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import Movie

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


class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'birth_date', 'is_private', 'bio']


# Optional to add 'validators': [validate_password] to 'password' params in extra_kwargs 
class UserSignUpSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'birth_date']
        extra_kwargs = {
            'password': {'write_only': True},
            'birth_date': {'required': True}
        }

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            birth_date=validated_data['birth_date']
        )
        user.set_password(validated_data['password'])
        user.save()
        return user

class DisplayMovieSerializer(serializers.ModelSerializer):
    class Meta:
        model = Movie
        fields = ['title', 'poster_path', 'overview', 'release_date', 'runtime', 'adult', 'tmdb_id']