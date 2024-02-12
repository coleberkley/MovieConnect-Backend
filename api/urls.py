from django.urls import path
from .views import (
    CreateGenericUserView, 
    CookieTokenObtainPairView, 
    CookieTokenRefreshView, 
    GenericUserProfileView, 
    LogoutView
    )

urlpatterns = [
    path('user/signup/', CreateGenericUserView.as_view(), name='user_signup'), # Create user
    path('token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'), # Obtain a new token when logging in
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'), # Refresh token if token expires
    path('user/logout/', LogoutView.as_view(), name='logout'),
    path('user/profile/', GenericUserProfileView.as_view(), name='user-profile'), # See user info
]
