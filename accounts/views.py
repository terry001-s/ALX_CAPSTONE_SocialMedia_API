from rest_framework import generics
from django.contrib.auth import get_user_model
from .serializers import UserSerializer

User = get_user_model()

class UserListCreateView(generics.ListCreateAPIView):
    """View to list all users or create new user"""
    queryset = User.objects.all()
    serializer_class = UserSerializer
    
    # For now, anyone can create an account
    # We'll add authentication later