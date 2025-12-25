from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostListCreateView, PostDetailView, UserPostsView,
    FollowViewSet, UserFollowDetailView,
    FeedView, GlobalFeedView,
    LikeView, UnlikeView, CommentListCreateView, CommentDetailView, ReplyCreateView  
)

from django.http import JsonResponse

# Create router for ViewSet
router = DefaultRouter()
router.register(r'follow', FollowViewSet, basename='follow')


def api_root(request):
    return JsonResponse({
        'message': 'Social Media API',
        'endpoints': {
            'accounts': {
                'register': '/api/accounts/register/',
                'login': '/api/accounts/login/',
                'my_profile': '/api/accounts/me/',
                'users_list': '/api/accounts/users/',
            },
            'posts': {
                'all_posts': '/api/posts/',
                'create_post': 'POST /api/posts/',
                'post_detail': '/api/posts/{id}/',
                'user_posts': '/api/posts/user/{username}/',
            },
            'follow': {
                'follow_user': 'POST /api/follow/follow/',
                'unfollow_user': 'POST /api/follow/unfollow/',
                'my_followers': '/api/follow/followers/',
                'my_following': '/api/follow/following/',
                'user_detail': '/api/users/{username}/',
            },
            'feed': {
                'personal_feed': '/api/feed/',
                'global_feed': '/api/feed/global/',
            },
            'interactions': {
                'like_post': 'POST /api/posts/{id}/likes/',
                'unlike_post': 'DELETE /api/posts/{id}/unlike/',
                'post_comments': '/api/posts/{id}/comments/',
                'comment_detail': '/api/comments/{id}/',
                'reply_to_comment': 'POST /api/comments/{id}/reply/',
            }
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    
    # Post endpoints
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/user/<str:username>/', UserPostsView.as_view(), name='user-posts'),
    
    # Follow endpoints
    path('', include(router.urls)),
    
    # User detail
    path('users/<str:username>/', UserFollowDetailView.as_view(), name='user-detail'),
    
    # Feed endpoints
    path('feed/', FeedView.as_view(), name='personal-feed'),
    path('feed/global/', GlobalFeedView.as_view(), name='global-feed'),
    
    # Like endpoints
    path('posts/<int:post_id>/likes/', LikeView.as_view(), name='post-likes'),
    path('posts/<int:post_id>/unlike/', UnlikeView.as_view(), name='post-unlike'),
    
    # Comment endpoints
    path('posts/<int:post_id>/comments/', CommentListCreateView.as_view(), name='post-comments'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
    path('comments/<int:comment_id>/reply/', ReplyCreateView.as_view(), name='comment-reply'),
]