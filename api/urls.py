from django.urls import path
from .views import (
    CreateGenericUserView, 
    CookieTokenObtainPairView, 
    CookieTokenRefreshView, 
    RetrieveUserProfile, 
    LogoutView,
    RetrieveMovies,
    RetrieveMovieDetail,
    MovieCommentsView,
    RateMovieView,
    CommentView,
    ListFriendsView,
    SendFriendRequestView,
    UpdateFriendRequestView,
    CancelFriendRequestView,
    ListIncomingFriendRequestsView,
    ListOutgoingFriendRequestsView,
    ListRatedMoviesView,
    ListUserRatedMoviesView,
    UserSearchView,
    MovieSearchView,
    UpdateProfileView,
    RemoveFriendView,
    RetrieveOtherUserProfile,
    ListUserFriendsView,
    DeleteUserView,
    MostPopularMoviesView,
    SimilarMoviesView,
    )

urlpatterns = [

    # Remember http:://localhost:80/api/ is the base URL for all of these endpoints. 
    # See mcbackend/urls.py for why /api/ is prepended to all these paths.
    
    # User Authentication
    path('user/signup/', CreateGenericUserView.as_view(), name='user_signup'), # Sign up
    path('token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'), # Sign in
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'), # Refresh token (Unused)
    path('user/logout/', LogoutView.as_view(), name='logout'), # Sign out
    path('user/delete/', DeleteUserView.as_view(), name='delete_user'), # Delete account

    # User Profile Page
    path('user/profile/', RetrieveUserProfile.as_view(), name='retrieve_user_profile'), # Get user data
    path('user/movies/rated/', ListRatedMoviesView.as_view(), name='list_rated_movies'), # Get rated movies list for signed-in user
    path('user/update/', UpdateProfileView.as_view(), name='update_profile'), # Update user profile
    path('friends/', ListFriendsView.as_view(), name='list_friends'), # Get friends list
    path('user/remove-friend/<int:friend_id>/', RemoveFriendView.as_view(), name='remove-friend'), # Remove friend
    path('friend-requests/incoming/', ListIncomingFriendRequestsView.as_view(), name='list_incoming_friend_requests'), # List incoming friend requests
    path('friend-requests/outgoing/', ListOutgoingFriendRequestsView.as_view(), name='list_outgoing_friend_requests'), # List outgoing friend requests
    path('friend-requests/update/<int:request_id>/', UpdateFriendRequestView.as_view(), name='update_friend_request'), # Accept/Reject friend request
    path('friend-requests/cancel/<int:request_id>/', CancelFriendRequestView.as_view(), name='cancel_friend_request'), # Cancel outgoing friend request

    # Movie Lists
    path('user/movies/', RetrieveMovies.as_view(), name='retrieve_movies'), # Get primary movie recommendation list for user
    path('movies/popular/', MostPopularMoviesView.as_view(), name='most_popular_movies'), # Get most popular movies

    # Searching
    path('movie/search/', MovieSearchView.as_view(), name='movie_search'), # Search for movies by title
    path('user/search/', UserSearchView.as_view(), name='user_search'), # Search for users by username

    # Movie Page
    path('movie/<int:pk>/', RetrieveMovieDetail.as_view(), name='retrieve_movie'), # Get movie details
    path('movie/<int:pk>/comments/', MovieCommentsView.as_view(), name='movie_comments'), # Get Movie comments
    path('movie/<int:pk>/similar/', SimilarMoviesView.as_view(), name='similar_movies'),  # Get similar movies
    path('movie/<int:pk>/rate/', RateMovieView.as_view(), name='rate_movie'), # Add/Update a movie rating
    path('movie/<int:pk>/comment/', CommentView.as_view(), name='movie_comment'), # Add/Delete comment on a movie

    # Other User Page
    path('user/<int:user_id>/profile/', RetrieveOtherUserProfile.as_view(), name='retrieve_other_user_profile'), # Get another user's profile
    path('user/<int:user_id>/friends/', ListUserFriendsView.as_view(), name='list_user_friends'), # Get friends list for another user
    path('user/<int:user_id>/movies/rated/', ListUserRatedMoviesView.as_view(), name='list_user_rated_movies'), # Get already-rated movies list for another user
    path('send-friend-request/<int:to_user_id>/', SendFriendRequestView.as_view(), name='send_friend_request'), # Send friend request
]
