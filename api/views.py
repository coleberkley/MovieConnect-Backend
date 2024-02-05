from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import GenericUserSerializer, UserNameSerializer
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView
from django.http import JsonResponse
from django.contrib.auth import get_user_model
from rest_framework import generics, permissions


# Create a Generic User
class CreateGenericUserView(APIView):

    def post(self, request, format='json'):

        serializer = GenericUserSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            if user:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Renders the current User
class GenericUserProfileView(generics.RetrieveAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Directly return the username in the response
        user_data = {'username': request.user.username}
        return Response(user_data)


# Custom Obtain/Refresh token responses to tell React frontend to store token in HttpOnly cookies
class CookieTokenObtainPairView(TokenObtainPairView):
    def finalize_response(self, request, response, *args, **kwargs):
        # Check if we have an access token in the response data
        if 'access' in response.data:
            # Set the access token in an HttpOnly cookie
            response.set_cookie(
                'access_token',
                response.data['access'],
                max_age=3600,  # Expires in 1 hour, adjust based on ACCESS_TOKEN_LIFETIME
                httponly=True,
                samesite='Lax',  # 'Strict' for strictest setting, 'None' if your frontend is on a different domain and you're using HTTPS
                secure=False  # Remember to set to True in production for HTTPS
            )
            # Optionally remove the access token from the response body to not expose it directly to the client
            del response.data['access']

        return super().finalize_response(request, response, *args, **kwargs)

class CookieTokenRefreshView(TokenRefreshView):
    def finalize_response(self, request, response, *args, **kwargs):
        # Check if we have an access token in the response data
        if 'access' in response.data:
            # Set the new access token in an HttpOnly cookie
            response.set_cookie(
                'access_token',
                response.data['access'],
                max_age=3600,  # Adjust based on your ACCESS_TOKEN_LIFETIME
                httponly=True,
                samesite='Lax',  # Or 'None' for cross-origin requests with HTTPS
                secure=False  # Set to True in production with HTTPS
            )
            # Optionally remove the access token from the response body
            del response.data['access']

        return super().finalize_response(request, response, *args, **kwargs)