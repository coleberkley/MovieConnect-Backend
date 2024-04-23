from rest_framework import status, generics, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from rest_framework_simplejwt.tokens import RefreshToken
from django.http import JsonResponse
from django.conf import settings
from .serializers import UserSignUpSerializer, UserProfileSerializer, DisplayMovieSerializer, MovieDetailSerializer, CommentSerializer, RatingSerializer, FriendRequestSerializer, UserNameSerializer, UserInfoSerializer, UpdateProfileSerializer, OtherUserProfileSerializer, UserRatedMoviesSerializer
from rest_framework.permissions import IsAuthenticated
from .models import Movie, Rating, Comment, FriendRequest
from django.db.models import Q
from rest_framework.exceptions import NotFound
from django.contrib.auth import get_user_model
from .algorithms.xgboost_w2v_opt import recommend_movies
from django.db.models import Avg

User = get_user_model()


### USER VIEWS ###

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


# Create a New User and Sign In
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
        else:
            print(serializer.errors)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Base class for setting cookies in token views
class TokenViewBaseMixin:
    def finalize_response(self, request, response, *args, **kwargs):
        if 'access' in response.data:
            set_access_token_cookie(response, response.data['access'])
            del response.data['access']
        return super().finalize_response(request, response, *args, **kwargs)


# Sign in view
class CookieTokenObtainPairView(TokenViewBaseMixin, TokenObtainPairView):
    pass


# Sign in refresh view (Not used)
class CookieTokenRefreshView(TokenViewBaseMixin, TokenRefreshView):
    pass


# Logout 
class LogoutView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        response = JsonResponse({"detail": "Successfully logged out."})
        response.delete_cookie('access_token')
        return response


# Delete User Account
class DeleteUserView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request):
        user = request.user
        try:
            # Deleting the user
            user.delete()
            response = JsonResponse({"detail": "User account deleted successfully."}, status=status.HTTP_204_NO_CONTENT)
            # Removing the authentication cookie
            response.delete_cookie('access_token')
            return response
        except Exception as e:
            return Response({"error": "Failed to delete user.", "details": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Retrieve User Data
class RetrieveUserProfile(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        serializer = UserProfileSerializer(request.user)
        return Response(serializer.data) 
    

# Update User Profile
class UpdateProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def put(self, request, *args, **kwargs):
        user = request.user
        serializer = UpdateProfileSerializer(user, data=request.data, partial=True)
        
        if serializer.is_valid():
            serializer.save()
            return Response({"message": "Profile updated successfully."}, status=status.HTTP_200_OK)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



### LIST VIEWS ###

# Retrieves the movie recommendation list for the user
class RetrieveMovies(APIView):
    permission_classes = [IsAuthenticated]
 
    def get(self, request):
        username = request.user.username
        recommended_titles = recommend_movies(username, top_n=10)
        movies = Movie.objects.filter(title__in=recommended_titles)
        serializer = DisplayMovieSerializer(movies, many=True)
        return Response(serializer.data)


# Retrieves the popular movies list for the user
class MostPopularMoviesView(APIView):
    permission_classes = [IsAuthenticated]

    # Currently returns 10 movies
    def get(self, request, format=None):
        number_of_movies = 20  
        popular_movies = Movie.objects.filter(avg_rating__isnull=False).order_by('-avg_rating')[:number_of_movies]
        serializer = DisplayMovieSerializer(popular_movies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Retrieves the similar movies list for a movie
class SimilarMoviesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk, format=None):
        try:
            movie = Movie.objects.get(pk=pk)
            similar_movies = movie.similar_movies.all()
            serializer = DisplayMovieSerializer(similar_movies, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Movie.DoesNotExist:
            return Response({'message': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)


# Retrieves the already-rated movies list for the user
class ListRatedMoviesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        # Find all ratings made by the user
        user_ratings = Rating.objects.filter(user=request.user).values_list('movie', flat=True)
        
        # Retrieve the corresponding movies
        rated_movies = Movie.objects.filter(id__in=user_ratings)
        
        # Serialize the movies
        serializer = UserRatedMoviesSerializer(rated_movies, many=True, context={'user': request.user})
        return Response(serializer.data)


# List all rated movies for another user
class ListUserRatedMoviesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        user_ratings = Rating.objects.filter(user=target_user).values_list('movie', flat=True)
        rated_movies = Movie.objects.filter(id__in=user_ratings)
        
        # Pass the target user to the serializer's context
        serializer = UserRatedMoviesSerializer(rated_movies, many=True, context={'user': target_user})
        return Response(serializer.data, status=status.HTTP_200_OK)


# Returns a search query list of movies by title (/api/movie/search?title=avengers)
class MovieSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search_query = request.query_params.get('title', '')
        if not search_query:
            return Response({'message': 'No search query provided.'}, status=status.HTTP_400_BAD_REQUEST)

        found_movies = Movie.objects.filter(title__icontains=search_query)
        serializer = DisplayMovieSerializer(found_movies, many=True)
        print(f"Found movies: {serializer.data}")
        return Response(serializer.data)


# Returns a list of movies in the user's watchlist
class ViewWatchlist(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        movies = request.user.watchlist.all()
        serializer = DisplayMovieSerializer(movies, many=True)
        return Response(serializer.data)



### MOVIE VIEWS ###

# Retrieve all movie details for displaying a single movie
class RetrieveMovieDetail(APIView):
    def get(self, request, pk, format=None):
        movie = Movie.objects.filter(pk=pk).first()
        if movie is not None:
            serializer = MovieDetailSerializer(movie, context={'request': request})
            print(f"Movie details: {serializer.data}")
            return Response(serializer.data)
        else:
            return Response({'message': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)


# Retrieve all comments for a given movie
class MovieCommentsView(APIView):
    def get(self, request, pk, format=None):
        comments = Comment.objects.filter(movie__id=pk).order_by('-timestamp')
        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data)


# Add or delete a comment for a movie
class CommentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, format=None):
        print(f"Request data: {request.data}")
        user = request.user
        try:
            movie = Movie.objects.get(pk=pk)
        except Movie.DoesNotExist:
            return Response({'message': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            Comment.objects.create(user=user, movie=movie, body=serializer.validated_data['body'])
            return Response({'message': 'Comment added successfully'}, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk, format=None):
        user = request.user
        comment_id = request.query_params.get('comment_id')
        if not comment_id:
            return Response({'message': 'Comment ID is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            comment = Comment.objects.get(pk=comment_id, user=user, movie_id=pk)
            comment.delete()
            return Response({'message': 'Comment deleted successfully'}, status=status.HTTP_204_NO_CONTENT)
        except Comment.DoesNotExist:
            return Response({'message': 'Comment not found or not owned by user'}, status=status.HTTP_404_NOT_FOUND)


# Rate a movie
class RateMovieView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk, format=None):
        user = request.user
        try:
            movie = Movie.objects.get(pk=pk)
        except Movie.DoesNotExist:
            return Response({'message': 'Movie not found'}, status=status.HTTP_404_NOT_FOUND)

        # Ensure the rating is provided in the request
        if 'rating' not in request.data:
            return Response({'message': 'Rating is required'}, status=status.HTTP_400_BAD_REQUEST)

        rating_value = request.data['rating']
        
        # Get or create the Rating instance
        rating_instance, created = Rating.objects.get_or_create(
            user=user, 
            movie=movie,
            defaults={'rating': rating_value}  # Set default rating if creating new
        )
        
        # If the rating instance was found and not created, update it
        if not created:
            rating_instance.rating = rating_value
            rating_instance.save()

        # Recalculate the average rating for the movie
        new_avg_rating = movie.movie_ratings.aggregate(Avg('rating'))['rating__avg']
        movie.avg_rating = new_avg_rating
        movie.save()

        # Serialize the rating instance
        serializer = RatingSerializer(rating_instance, context={'request': request})
        return Response({'message': 'Rating submitted successfully', 'data': serializer.data}, status=status.HTTP_201_CREATED if created else status.HTTP_200_OK)


# Add or remove a movie from the user's watchlist
class ManageWatchlistView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        try:
            movie = Movie.objects.get(pk=pk)
            request.user.watchlist.add(movie)
            return Response({'message': 'Movie added to watchlist.'}, status=status.HTTP_201_CREATED)
        except Movie.DoesNotExist:
            return Response({'message': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            movie = Movie.objects.get(pk=pk)
            request.user.watchlist.remove(movie)
            return Response({'message': 'Movie removed from watchlist.'}, status=status.HTTP_204_NO_CONTENT)
        except Movie.DoesNotExist:
            return Response({'message': 'Movie not found.'}, status=status.HTTP_404_NOT_FOUND)




### FRIEND VIEWS ###

# Search for users by username (/api/user/search?username=johndoe)
class UserSearchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        search_query = request.query_params.get('username', '')
        if not search_query:
            return Response({'message': 'No search query provided.'}, status=status.HTTP_400_BAD_REQUEST)

        # Find users whose username contains the search_query
        found_users = User.objects.filter(username__icontains=search_query)
        serializer = UserInfoSerializer(found_users, many=True)
        print(f"Found users: {serializer.data}")
        return Response(serializer.data)


# Retrieve another user's profile
class RetrieveOtherUserProfile(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            user = User.objects.get(pk=user_id)
            if request.user.id == user_id:  
                return Response({'message': 'Use the retrieve_user_profile endpoint for own profile.'}, status=status.HTTP_400_BAD_REQUEST)

            context = {'request': request}
            serializer = OtherUserProfileSerializer(user, context=context)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except User.DoesNotExist:
            return Response({'message': 'User not found'}, status=status.HTTP_404_NOT_FOUND)


# Send a friend request
class SendFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, to_user_id):
        print(f"Request data: {request.data}")
        from_user = request.user
        if from_user.id == to_user_id:
            return Response({'message': 'You cannot send a friend request to yourself.'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            to_user = User.objects.get(pk=to_user_id)
            # Check if a friend request already exists
            if FriendRequest.objects.filter(from_user=from_user, to_user=to_user).exists() or FriendRequest.objects.filter(from_user=to_user, to_user=from_user, accepted=True).exists():
                return Response({'message': 'Friend request already sent or you are already friends.'}, status=status.HTTP_409_CONFLICT)

            FriendRequest.objects.create(from_user=from_user, to_user=to_user, accepted=False)
            return Response({'message': 'Friend request sent successfully.'}, status=status.HTTP_201_CREATED)

        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)


# Remove a friend
class RemoveFriendView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, friend_id):
        print(f"Request data: {request.data}")
        user = request.user
        # Attempt to find an accepted friend request in either direction.
        friend_request = FriendRequest.objects.filter(
            (Q(from_user=user, to_user_id=friend_id) | Q(from_user_id=friend_id, to_user=user)),
            accepted=True
        ).first()

        if not friend_request:
            return Response({"message": "Friendship not found."}, status=status.HTTP_404_NOT_FOUND)

        friend_request.delete()
        return Response({"message": "Friendship removed successfully."}, status=status.HTTP_204_NO_CONTENT)


# Returns a list of friends (user ids and usernames) for the signed in user
class ListFriendsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # Get all users who sent a friend request to the user and was accepted
        friends_from_requests = User.objects.filter(
            received_requests__from_user=user,
            received_requests__accepted=True
        )

        # Get all users to whom the user sent a friend request and was accepted
        friends_to_requests = User.objects.filter(
            sent_requests__to_user=user,
            sent_requests__accepted=True
        )

        # Combine and deduplicate the two lists
        friends = (friends_from_requests | friends_to_requests).distinct()

        serializer = UserInfoSerializer(friends, many=True)
        return Response(serializer.data)


# Returns a list of friends (user ids and usernames) for a given user
class ListUserFriendsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, user_id):
        try:
            target_user = User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return Response({'message': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)

        # Get all users who have accepted a friend request from or to the target user
        friends_from_requests = User.objects.filter(
            received_requests__from_user=target_user,
            received_requests__accepted=True
        )

        friends_to_requests = User.objects.filter(
            sent_requests__to_user=target_user,
            sent_requests__accepted=True
        )

        # Combine and deduplicate the two lists
        friends = (friends_from_requests | friends_to_requests).distinct()

        serializer = UserInfoSerializer(friends, many=True)
        return Response(serializer.data)


# Accept or Deny an incoming friend request
class UpdateFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, request_id):
        print(f"Update Friend Request. Request data: {request.data}")
        try:
            friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
            friend_request.accepted = True
            friend_request.save()
            return Response({'message': 'Friend request accepted.'}, status=status.HTTP_200_OK)
        except FriendRequest.DoesNotExist:
            return Response({'message': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, request_id):
        print(f"Delete Friend Request. Request data: {request.data}")
        try:
            friend_request = FriendRequest.objects.get(id=request_id, to_user=request.user)
            friend_request.delete()
            return Response({'message': 'Friend request denied.'}, status=status.HTTP_204_NO_CONTENT)
        except FriendRequest.DoesNotExist:
            return Response({'message': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)


# Cancel an outgoing friend request
class CancelFriendRequestView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, request_id):
        print(f"Request data: {request.data}")
        try:
            friend_request = FriendRequest.objects.get(id=request_id, from_user=request.user)
            friend_request.delete()
            return Response({'message': 'Friend request canceled.'}, status=status.HTTP_204_NO_CONTENT)
        except FriendRequest.DoesNotExist:
            return Response({'message': 'Friend request not found.'}, status=status.HTTP_404_NOT_FOUND)


# List all incoming friend requests for the signed in user
class ListIncomingFriendRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        incoming_requests = FriendRequest.objects.filter(to_user=request.user, accepted=False)
        serializer = FriendRequestSerializer(incoming_requests, many=True)
        return Response(serializer.data)


# List all outgoing friend requests for the signed in user
class ListOutgoingFriendRequestsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        outgoing_requests = FriendRequest.objects.filter(from_user=request.user, accepted=False)
        serializer = FriendRequestSerializer(outgoing_requests, many=True)
        return Response(serializer.data)

