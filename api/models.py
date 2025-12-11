# api/models.py
from django.db import models
from django.conf import settings  # To reference our custom User model

class Post(models.Model):
    """
    A Post model - represents user's posts in our social media.
    Think: Twitter tweet, Facebook post, Instagram photo with caption.
    """
    
    # Every post needs an author (who created it)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,  # Reference to our custom User
        on_delete=models.CASCADE,  # If user is deleted, delete their posts
        related_name='posts'       # User.posts.all() gets user's posts
    )
    
    # The main content (text)
    content = models.TextField(
        max_length=1000,           # Character limit
        help_text="What's on your mind? (max 1000 chars)"
    )
    
    # Optional image URL
    image = models.URLField(
        blank=True,                # Not required
        null=True,                 # Can be empty in database
        help_text="Optional image URL"
    )
    
    # Automatic timestamps
    created_at = models.DateTimeField(auto_now_add=True)  # Set on creation
    updated_at = models.DateTimeField(auto_now=True)      # Update on save
    
    # Optional: Soft delete (mark as deleted instead of actually deleting)
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        """Extra model settings"""
        ordering = ['-created_at']  # Show newest posts first
        verbose_name = 'Post'
        verbose_name_plural = 'Posts'
    
    def __str__(self):
        """How post appears in admin panel"""
        return f"{self.user.username}: {self.content[:50]}..."
    
    @property
    def likes_count(self):
        """Count of likes on this post"""
        return self.likes.count()  # We'll add likes model later
    
    @property
    def comments_count(self):
        """Count of comments on this post"""
        return self.comments.count()  # We'll add comments model later