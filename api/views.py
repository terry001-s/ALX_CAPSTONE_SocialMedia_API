from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Post,Follow
from .serializers import PostSerializer, FollowSerializer, User, UserDetailSerializer
from accounts.permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet

class PostListCreateView(generics.ListCreateAPIView):
    """
    View to list all posts or create new post.
    GET: List all posts
    POST: Create new post (authenticated users only)
    """
    
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get posts, excluding deleted ones"""
        return Post.objects.filter(is_deleted=False)
    
    def perform_create(self, serializer):
        """Automatically set the post author to current user"""
        serializer.save(user=self.request.user)


class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    View to retrieve, update, or delete a single post.
    GET: Get post details
    PUT/PATCH: Update post
    DELETE: Delete post (soft delete)
    """
    
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated, IsOwnerOrReadOnly]
    queryset = Post.objects.filter(is_deleted=False)
    
    def get_object(self):
        """Get the post object, check permissions"""
        post = get_object_or_404(Post, pk=self.kwargs['pk'], is_deleted=False)
        
        # Check if user owns the post (for updates/deletes)
        self.check_object_permissions(self.request, post)
        
        return post
    
    def perform_update(self, serializer):
        """Update post - only owner can do this"""
        if serializer.instance.user != self.request.user:
            raise PermissionDenied("You can only edit your own posts.")
        serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete instead of actual delete"""
        instance.is_deleted = True
        instance.save()
        
        return Response(
            {"message": "Post deleted successfully."},
            status=status.HTTP_200_OK
        )


class UserPostsView(generics.ListAPIView):
    """
    View to list posts from a specific user.
    GET: Get all posts by a specific user
    """
    
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get posts by specific user"""
        username = self.kwargs['username']
        return Post.objects.filter(
            user__username=username,
            is_deleted=False
        ).select_related('user')  # Optimize database query
    

class FollowViewSet(ViewSet):
    """
    ViewSet for follow/unfollow operations.
    ViewSet gives us: /follow/ and /follow/{pk}/
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    @action(detail=False, methods=['POST'])
    def follow(self, request):
        """Follow a user"""
        username = request.data.get('username')
        
        if not username:
            return Response(
                {"error": "Username is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_follow = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if trying to follow self
        if request.user == user_to_follow:
            return Response(
                {"error": "You cannot follow yourself."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if already following
        if Follow.objects.filter(follower=request.user, following=user_to_follow).exists():
            return Response(
                {"error": "You are already following this user."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create follow
        follow = Follow.objects.create(
            follower=request.user,
            following=user_to_follow
        )
        
        serializer = FollowSerializer(follow, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['POST'])
    def unfollow(self, request):
        """Unfollow a user"""
        username = request.data.get('username')
        
        if not username:
            return Response(
                {"error": "Username is required."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            user_to_unfollow = User.objects.get(username=username)
        except User.DoesNotExist:
            return Response(
                {"error": "User not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Find and delete follow
        follow = Follow.objects.filter(
            follower=request.user,
            following=user_to_unfollow
        ).first()
        
        if not follow:
            return Response(
                {"error": "You are not following this user."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        follow.delete()
        
        return Response(
            {"message": f"You have unfollowed {username}."},
            status=status.HTTP_200_OK
        )
    
    @action(detail=False, methods=['GET'])
    def followers(self, request):
        """Get list of my followers"""
        followers = User.objects.filter(following__follower=request.user)
        serializer = UserDetailSerializer(
            followers, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def following(self, request):
        """Get list of people I follow"""
        following = User.objects.filter(followers__follower=request.user)
        serializer = UserDetailSerializer(
            following, 
            many=True,
            context={'request': request}
        )
        return Response(serializer.data)


class UserFollowDetailView(generics.RetrieveAPIView):
    """Get detailed user info with follow status"""
    
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    lookup_field = 'username'
    
    def get_serializer_context(self):
        context = super().get_serializer_context()
        context['request'] = self.request
        return context    