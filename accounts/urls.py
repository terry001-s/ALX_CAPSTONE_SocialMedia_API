from django.urls import path
from .views import (
    UserListCreateView,
    RegisterView, 
    LoginView, 
    UserProfileView, 
    UserDetailView,
    UserListView
)
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('users/', UserListCreateView.as_view(), name='user-list'),

    # Authentication
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    
    # User profiles
    path('me/', UserProfileView.as_view(), name='my-profile'),
    path('users/', UserListView.as_view(), name='user-list'),
    path('users/<str:username>/', UserDetailView.as_view(), name='user-detail'),
]