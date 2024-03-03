from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.conf import settings
from .serializers import UserSignUpSerializer, UserProfileSerializer, DisplayMovieSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Movie

# Utility function to set the HttpOnly cookie
def set_access_token_cookie(response, access_token):
    max_age = settings.SIMPLE_JWT['ACCESS_TOKEN_LIFETIME'].total_seconds()
    response.set_cookie(
        'access_token',
        access_token,
        max_age=max_age,
        httponly=True,
        samesite='Lax',  # Or 'Strict' for more constrained environments
        secure=False  # Remember to set to True in production
    )

# Create a Generic User
class CreateGenericUserView(APIView):

    def post(self, request, format='json'):
        serializer = UserSignUpSerializer(data=request.data)

        if serializer.is_valid():
            user = serializer.save()
            refresh = RefreshToken.for_user(user)  # Create a new token
            response = Response({
                "refresh": str(refresh), # Probably won't need to use this unless we want token expiration
                "detail": "User created and signed in successfully."
            }, status=status.HTTP_201_CREATED)
            set_access_token_cookie(response, str(refresh.access_token))
            return response
        
        error_detail = {'detail': 'Invalid data received.'}
        # error_detail.update(errors=serializer.errors)
        return Response(error_detail, status=status.HTTP_400_BAD_REQUEST)

# Retrieve User Data
class RetrieveUserProfile(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data)  

# Sends over a list of 10 movies from the database for now
class RetrieveMovies(APIView):
    permission_classes = [IsAuthenticated]  # Adjust permissions as needed

    def get(self, request):
        # Fetch the first 10 movies from the database
        movies = Movie.objects.all()[:10]
        # Serialize the movie data
        serializer = DisplayMovieSerializer(movies, many=True)
        return Response(serializer.data)


# Base class for setting cookies in token views
class TokenViewBaseMixin:
    def finalize_response(self, request, response, *args, **kwargs):
        if 'access' in response.data:
            set_access_token_cookie(response, response.data['access'])
            del response.data['access']
        return super().finalize_response(request, response, *args, **kwargs)

# Custom Obtain token response to tell React frontend to store token in HttpOnly cookies
class CookieTokenObtainPairView(TokenViewBaseMixin, TokenObtainPairView):
    pass

# Custom Refresh token response
class CookieTokenRefreshView(TokenViewBaseMixin, TokenRefreshView):
    pass

# Logout view
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = JsonResponse({"detail": "Successfully logged out."})
        response.delete_cookie('access_token')
        return response
