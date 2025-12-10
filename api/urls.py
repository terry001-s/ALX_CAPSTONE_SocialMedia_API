# api/urls.py
from django.urls import path
from rest_framework import routers
from django.http import JsonResponse

def api_root(request):
    """Root endpoint to show available API paths"""
    return JsonResponse({
        'message': 'Social Media API',
        'endpoints': {
            'accounts': '/api/accounts/',
            'auth': {
                'register': '/api/accounts/register/',
                'login': '/api/accounts/login/',
                'refresh_token': '/api/accounts/token/refresh/'
            },
            'user_profile': '/api/accounts/me/',
            'users': '/api/accounts/users/',
        },
        'documentation': 'Coming soon!'
    })

urlpatterns = [
    path('', api_root, name='api-root'),
]