from rest_framework import generics, permissions, status, serializers,filters 
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from rest_framework.views import APIView 
from .models import Notification, Post, Follow, Like, Comment  
from .serializers import PostSerializer, FollowSerializer, User, UserDetailSerializer, LikeSerializer, CommentSerializer, NotificationSerializer  
from accounts.permissions import IsOwnerOrReadOnly
from rest_framework.decorators import action
from rest_framework.viewsets import ViewSet
from django.core.paginator import Paginator
from django.db.models import Q 
from .filters import PostFilter, UserFilter
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import filters
from django.contrib.auth import get_user_model 

User = get_user_model()

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
    serializer_class = UserDetailSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = User.objects.all()
    lookup_field = 'username'
    
    def retrieve(self, request, *args, **kwargs):
        """Enhanced response with feed stats"""
        response = super().retrieve(request, *args, **kwargs)
        
        user = self.get_object()
        
        # Add feed-related stats
        response.data['feed_stats'] = {
            'total_posts': user.posts_count,
            'posts_in_your_feed': Post.objects.filter(
                user=user,
                is_deleted=False,
                user__followers__follower=request.user
            ).count() if request.user != user else 'N/A (your own profile)',
            'would_see_in_feed': request.user.is_following(user)
        }
        
        return response
    

class FeedView(generics.ListAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        user = self.request.user
        
        # Get base queryset
        posts = Post.objects.filter(
            Q(user__followers__follower=user) | Q(user=user),
            is_deleted=False
        ).select_related('user').order_by('-created_at')
        
        # Filter by date if provided
        date_from = self.request.query_params.get('date_from', None)
        date_to = self.request.query_params.get('date_to', None)
        
        if date_from:
            posts = posts.filter(created_at__gte=date_from)  # gte = greater than or equal
        if date_to:
            posts = posts.filter(created_at__lte=date_to)    # lte = less than or equal
        
        # Filter by user if provided
        username = self.request.query_params.get('user', None)
        if username:
            posts = posts.filter(user__username=username)
        
        # Filter by keyword/search
        search = self.request.query_params.get('search', None)
        if search:
            posts = posts.filter(content__icontains=search)  # Case-insensitive
        
        return posts
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Pagination
        page_size = int(request.query_params.get('page_size', 10))
        page_number = int(request.query_params.get('page', 1))
        
        paginator = Paginator(queryset, page_size)
        
        try:
            page = paginator.page(page_number)
        except:
            return Response(
                {"error": "Invalid page number."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(page.object_list, many=True)
        
        return Response({
            'feed_info': {
                'user': request.user.username,
                'following_count': request.user.following_count,
                'posts_in_feed': paginator.count,
            },
            'pagination': {
                'count': paginator.count,
                'page_size': page_size,
                'total_pages': paginator.num_pages,
                'current_page': page_number,
                'next_page': page.next_page_number() if page.has_next() else None,
                'previous_page': page.previous_page_number() if page.has_previous() else None,
                'has_next': page.has_next(),
                'has_previous': page.has_previous(),
            },
            'filters_applied': {
                'date_from': request.query_params.get('date_from'),
                'date_to': request.query_params.get('date_to'),
                'user': request.query_params.get('user'),
                'search': request.query_params.get('search'),
            },
            'posts': serializer.data
        })
    


class GlobalFeedView(generics.ListAPIView):
    """
    Global feed - all public posts (from all users)
    GET: Get paginated feed of all posts
    """
    
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get all public posts"""
        return Post.objects.filter(
            is_deleted=False
        ).select_related('user').order_by('-created_at')
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Pagination
        page_size = int(request.query_params.get('page_size', 20))
        page_number = int(request.query_params.get('page', 1))
        
        paginator = Paginator(queryset, page_size)
        
        try:
            page = paginator.page(page_number)
        except:
            return Response(
                {"error": "Invalid page number."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        serializer = self.get_serializer(page.object_list, many=True)
        
        return Response({
            'feed_type': 'global',
            'pagination': {
                'count': paginator.count,
                'total_pages': paginator.num_pages,
                'current_page': page_number,
            },
            'posts': serializer.data
        })    
    

class LikeView(generics.ListCreateAPIView):
    """
    Handle likes on posts.
    GET: Get all likes for a post
    POST: Like a post
    """
    
    serializer_class = LikeSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get likes for a specific post"""
        post_id = self.kwargs.get('post_id')
        return Like.objects.filter(post_id=post_id).select_related('user')
    
    def create(self, request, *args, **kwargs):
        """Like a post"""
        post_id = kwargs.get('post_id')
        
        try:
            post = Post.objects.get(id=post_id, is_deleted=False)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already liked
        if Like.objects.filter(user=request.user, post=post).exists():
            return Response(
                {"error": "You have already liked this post."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create like
        like = Like.objects.create(user=request.user, post=post)
        serializer = self.get_serializer(like)
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)


class UnlikeView(generics.DestroyAPIView):
    """
    Unlike a post.
    DELETE: Remove like from post
    """
    
    permission_classes = [permissions.IsAuthenticated]
    
    def delete(self, request, *args, **kwargs):
        post_id = kwargs.get('post_id')
        
        try:
            post = Post.objects.get(id=post_id, is_deleted=False)
        except Post.DoesNotExist:
            return Response(
                {"error": "Post not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Find and delete like
        like = Like.objects.filter(user=request.user, post=post).first()
        
        if not like:
            return Response(
                {"error": "You have not liked this post."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        like.delete()
        
        return Response(
            {"message": "Post unliked successfully."},
            status=status.HTTP_200_OK
        )


class CommentListCreateView(generics.ListCreateAPIView):
    """
    Handle comments on posts.
    GET: Get all comments for a post
    POST: Add comment to post
    """
    
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        """Get comments for a specific post"""
        post_id = self.kwargs.get('post_id')
        return Comment.objects.filter(
            post_id=post_id,
            is_deleted=False,
            parent__isnull=True  # Only top-level comments (not replies)
        ).select_related('user').prefetch_related('replies').order_by('created_at')
    
    def perform_create(self, serializer):
        """Create comment - set post from URL"""
        post_id = self.kwargs.get('post_id')
        post = Post.objects.get(id=post_id)
        serializer.save(user=self.request.user, post=post)


class CommentDetailView(generics.RetrieveUpdateDestroyAPIView):
    """
    Handle single comment operations.
    GET: Get comment details
    PUT/PATCH: Update comment
    DELETE: Delete comment (soft delete)
    """
    
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    queryset = Comment.objects.filter(is_deleted=False)
    
    def get_object(self):
        """Get comment, check permissions"""
        comment = super().get_object()
        
        # Check if user owns the comment (for updates/deletes)
        if self.request.user != comment.user:
            raise PermissionDenied("You can only edit your own comments.")
        
        return comment
    
    def perform_update(self, serializer):
        """Update comment"""
        serializer.save()
    
    def perform_destroy(self, instance):
        """Soft delete comment"""
        instance.is_deleted = True
        instance.save()
        
        return Response(
            {"message": "Comment deleted successfully."},
            status=status.HTTP_200_OK
        )


class ReplyCreateView(generics.CreateAPIView):
    """
    Create a reply to a comment.
    POST: Add reply to a comment
    """
    
    serializer_class = CommentSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def create(self, request, *args, **kwargs):
        """Create a reply to a comment"""
        comment_id = kwargs.get('comment_id')
        
        try:
            parent_comment = Comment.objects.get(id=comment_id, is_deleted=False)
        except Comment.DoesNotExist:
            return Response(
                {"error": "Comment not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Create reply
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Set parent and post automatically
        serializer.save(
            user=request.user,
            post=parent_comment.post,
            parent=parent_comment
        )
        
        return Response(serializer.data, status=status.HTTP_201_CREATED)    
    

class PostListCreateView(generics.ListCreateAPIView):
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    # Add filter backends
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_class = PostFilter
    search_fields = ['content', 'user__username']
    ordering_fields = ['created_at', 'updated_at', 'likes_count']
    ordering = ['-created_at']  # Default ordering
    
    def get_queryset(self):
        return Post.objects.filter(is_deleted=False).select_related('user')    
    


class NotificationListView(generics.ListAPIView):
    """Get user's notifications"""
    
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer 
    
    def get_queryset(self):
        return Notification.objects.filter(
            user=self.request.user
        ).select_related('related_user', 'related_post', 'related_comment')
    
    def list(self, request, *args, **kwargs):
        queryset = self.filter_queryset(self.get_queryset())
        
        # Mark all as read if requested
        mark_read = request.query_params.get('mark_read', '').lower() == 'true'
        if mark_read:
            queryset.update(is_read=True)
        
        # Prepare response
        notifications = []
        for notification in queryset:
            notifications.append({
                'id': notification.id,
                'type': notification.type,
                'message': notification.message,
                'is_read': notification.is_read,
                'created_at': notification.created_at,
                'related_user': {
                    'username': notification.related_user.username if notification.related_user else None,
                    'profile_picture': notification.related_user.profile_picture if notification.related_user else None,
                } if notification.related_user else None,
                'related_post_id': notification.related_post.id if notification.related_post else None,
                'related_comment_id': notification.related_comment.id if notification.related_comment else None,
            })
        
        # Count unread
        unread_count = queryset.filter(is_read=False).count()
        
        return Response({
            'unread_count': unread_count,
            'total_count': queryset.count(),
            'notifications': notifications[:50]  # Limit to 50
        })


class NotificationDetailView(APIView):
    """Mark notification as read"""
    
    permission_classes = [permissions.IsAuthenticated]
    
    def patch(self, request, pk):
        try:
            notification = Notification.objects.get(pk=pk, user=request.user)
            notification.mark_as_read()
            
            return Response({
                'message': 'Notification marked as read',
                'notification_id': notification.id
            })
            
        except Notification.DoesNotExist:
            return Response(
                {'error': 'Notification not found'},
                status=status.HTTP_404_NOT_FOUND
            )    