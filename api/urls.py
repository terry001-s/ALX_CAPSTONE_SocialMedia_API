from django.urls import path
from .views import PostListCreateView, PostDetailView, UserPostsView
from django.http import JsonResponse

def api_root(request):
    """Root endpoint to show available API paths"""
    return JsonResponse({
        'message': 'Social Media API',
        'endpoints': {
            'accounts': {
                'register': '/api/accounts/register/',
                'login': '/api/accounts/login/',
                'my_profile': '/api/accounts/me/',
                'users': '/api/accounts/users/',
            },
            'posts': {
                'all_posts': '/api/posts/',
                'create_post': 'POST /api/posts/',
                'post_detail': '/api/posts/{id}/',
                'user_posts': '/api/posts/user/{username}/',
            },
            'documentation': 'Coming soon!'
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    
    # Post endpoints
    path('posts/', PostListCreateView.as_view(), name='post-list-create'),
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),
    path('posts/user/<str:username>/', UserPostsView.as_view(), name='user-posts'),
]