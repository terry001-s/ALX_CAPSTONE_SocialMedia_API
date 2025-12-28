from warnings import filters
from rest_framework import generics, status, permissions

from api.filters import UserFilter
from .permissions import IsPublicEndpoint, IsOwnerOrReadOnly
from django.contrib.auth import get_user_model
from .serializers import UserSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from .serializers import RegisterSerializer, LoginSerializer, UserProfileSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend


User = get_user_model()

class UserListView(generics.ListAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Add filters
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = UserFilter
    search_fields = ['username', 'bio']
    ordering_fields = ['username', 'date_joined', 'followers_count']
    ordering = ['username']  # Default ordering
    
    def get_queryset(self):
        return User.objects.all()


class RegisterView(APIView):
    """View for user registration"""
    
    permission_classes = [IsPublicEndpoint]  # Anyone can register
    
    def post(self, request):
        serializer = RegisterSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.save()
            
            # Create JWT tokens for the new user
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserProfileSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'User created successfully!'
            }, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class LoginView(APIView):
    """View for user login"""
    
    permission_classes = [IsPublicEndpoint]  # Anyone can login
    
    def post(self, request):
        serializer = LoginSerializer(data=request.data)
        
        if serializer.is_valid():
            user = serializer.validated_data['user']
            
            # Create JWT tokens
            refresh = RefreshToken.for_user(user)
            
            return Response({
                'user': UserProfileSerializer(user).data,
                'refresh': str(refresh),
                'access': str(refresh.access_token),
                'message': 'Login successful!'
            }, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(generics.RetrieveUpdateAPIView):
    """View to see and update user profile"""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    
    def get_object(self):
        # Always return the current user
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        # Remove password from update data (we'll handle separately)
        if 'password' in request.data:
            request.data.pop('password')
        
        return super().update(request, *args, **kwargs)


class UserDetailView(generics.RetrieveAPIView):
    """View to see other users' profiles (read-only)"""
    
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    lookup_field = 'username'  # Use username instead of ID in URL
    
    def get_serializer_context(self):
        # Add request context for serializers
        return {'request': self.request}


