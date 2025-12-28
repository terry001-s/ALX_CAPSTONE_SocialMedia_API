import django_filters
from django.contrib.auth import get_user_model
from django.db import models
from .models import Post

User = get_user_model()

class PostFilter(django_filters.FilterSet):
    """Filters for posts"""
    
    content = django_filters.CharFilter(lookup_expr='icontains')
    username = django_filters.CharFilter(field_name='user__username', lookup_expr='icontains')
    date_from = django_filters.DateFilter(field_name='created_at', lookup_expr='gte')
    date_to = django_filters.DateFilter(field_name='created_at', lookup_expr='lte')
    has_image = django_filters.BooleanFilter(field_name='image', lookup_expr='isnull', exclude=True)
    
    class Meta:
        model = Post
        fields = ['content', 'username', 'date_from', 'date_to', 'has_image']


class UserFilter(django_filters.FilterSet):
    """Filters for users"""
    
    username = django_filters.CharFilter(lookup_expr='icontains')
    bio = django_filters.CharFilter(lookup_expr='icontains')
    joined_after = django_filters.DateFilter(field_name='date_joined', lookup_expr='gte')
    joined_before = django_filters.DateFilter(field_name='date_joined', lookup_expr='lte')
    min_followers = django_filters.NumberFilter(method='filter_min_followers')
    min_following = django_filters.NumberFilter(method='filter_min_following')
    
    class Meta:
        model = User
        fields = ['username', 'bio']
    
    def filter_min_followers(self, queryset, name, value):
        """Filter users with at least X followers"""
        return queryset.annotate(
            follower_count=models.Count('followers')
        ).filter(follower_count__gte=value)
    
    def filter_min_following(self, queryset, name, value):
        """Filter users following at least X people"""
        return queryset.annotate(
            following_count=models.Count('following')
        ).filter(following_count__gte=value)