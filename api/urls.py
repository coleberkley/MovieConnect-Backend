from django.urls import path
from .views import CreateGenericUserView
from .views import CookieTokenObtainPairView
from .views import CookieTokenRefreshView
from .views import GenericUserProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('user/signup/', CreateGenericUserView.as_view(), name='user_signup'), # Create user
    path('token/', CookieTokenObtainPairView.as_view(), name='token_obtain_pair'), # Obtain a new token when logging in
    path('token/refresh/', CookieTokenRefreshView.as_view(), name='token_refresh'), # Refresh token if token expires
    path('user/profile/', GenericUserProfileView.as_view(), name='user-profile'), # See user info
]
