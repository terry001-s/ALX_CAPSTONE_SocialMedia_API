from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    """Custom User model that extends Django's built-in User"""
    
    # Add extra fields to the standard User model
    bio = models.TextField(max_length=500, blank=True)
    profile_picture = models.URLField(blank=True, help_text="Link to profile image")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return self.username  # Shows username in admin panel
    
    @property
    def followers_count(self):
        """Returns number of followers"""
        return self.followers.count()
    
    @property
    def following_count(self):
        """Returns number of people this user follows"""
        return self.following.count()