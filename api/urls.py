from django.urls import path
from .views import (
    CreateGenericUserView, 
    CookieTokenObtainPairView, 
    CookieTokenRefreshView, 
    RetrieveUserProfile, 
    LogoutView,
    RetrieveMovies
    )

urlpatterns = [
    path('user/signup/', CreateGenericUserView.as_view(), name='user_signup'), # Create user
    path('token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'), # Obtain a new token when logging in
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'), # Refresh token if token expires
    path('user/logout/', LogoutView.as_view(), name='logout'),
    path('user/userprofile/', RetrieveUserProfile.as_view(), name='retrieve_user_profile'),
    path('user/movies/', RetrieveMovies.as_view(), name='retrieve_movies'),

]
