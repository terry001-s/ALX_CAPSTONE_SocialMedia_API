from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    PostListCreateView, PostDetailView, UserPostsView,
    FollowViewSet, UserFollowDetailView  
)
from django.http import JsonResponse

# Create router for ViewSet
router = DefaultRouter()
router.register(r'follow', FollowViewSet, basename='follow')


def api_root(request):
    """Root endpoint to show available API paths"""
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
            }
        },
        'note': 'All endpoints require Authorization: Bearer <token> except register/login'
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    
    # Post endpoints
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/user/<str:username>/', UserPostsView.as_view(), name='user-posts'),

       # Follow endpoints (via router)
    path('', include(router.urls)),
    
    # User detail with follow info
    path('users/<str:username>/', UserFollowDetailView.as_view(), name='user-detail'),
]