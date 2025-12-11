# accounts/models.py - Update User class
from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username
    
    @property
    def followers_count(self):
        """Get number of followers"""
        return self.followers.count()  # From Follow model's related_name
    
    @property
    def following_count(self):
        """Get number of people I follow"""
        return self.following.count()  # From Follow model's related_name
    
    @property
    def posts_count(self):
        """Get number of posts by this user"""
        return self.posts.count()  # From Post model's related_name
    
    def is_following(self, user):
        """Check if this user is following another user"""
        return self.following.filter(following=user).exists()
    
    def is_followed_by(self, user):
        """Check if this user is followed by another user"""
        return self.followers.filter(follower=user).exists()