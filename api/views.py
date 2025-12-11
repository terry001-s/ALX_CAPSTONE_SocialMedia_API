from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from .models import Post
from .serializers import PostSerializer
from accounts.permissions import IsOwnerOrReadOnly

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