from django.db import models
from django.conf import settings
from django.forms import ValidationError  # To reference our custom User model

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
        null=True,                 
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
    

class Follow(models.Model):
    """
    Model for following relationships.
    When User A follows User B, we create: follower=A, following=B
    """
    
    # Who is doing the following
    follower = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='following'  # user.following.all() = people I follow
    )
    
    # Who is being followed
    following = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='followers'  # user.followers.all() = my followers
    )
    
    # When the follow happened
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """Ensure unique follow relationships"""
        unique_together = ['follower', 'following']  # Can't follow same person twice
        ordering = ['-created_at']  # Newest follows first
        verbose_name = 'Follow Relationship'
        verbose_name_plural = 'Follow Relationships'
    
    def __str__(self):
        """How it appears in admin panel"""
        return f"{self.follower.username} follows {self.following.username}"
    
    def clean(self):
        """Validate before saving"""
        # Prevent users from following themselves
        if self.follower == self.following:
            raise ValidationError("Users cannot follow themselves.")
    
    def save(self, *args, **kwargs):
        """Custom save to run validation"""
        self.clean()  # Run validation
        super().save(*args, **kwargs)  # Call original save method



class Like(models.Model):
    """
    Model for post likes.
    When User A likes Post B, we create: user=A, post=B
    """
    
    # Who liked the post
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='likes'  # user.likes.all() = posts I liked
    )
    
    # Which post was liked
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='likes'  # post.likes.all() = users who liked this
    )
    
    # When the like happened
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        """Ensure unique likes (can't like same post twice)"""
        unique_together = ['user', 'post']  # One like per user per post
        ordering = ['-created_at']
        verbose_name = 'Like'
        verbose_name_plural = 'Likes'
    
    def __str__(self):
        return f"{self.user.username} likes post #{self.post.id}"
    
    def clean(self):
        """Validate before saving"""
        # User can't like their own post? (Let's allow it for now)
        # You could add: if self.user == self.post.user
        pass
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)


class Comment(models.Model):
    """
    Model for post comments.
    Users can comment on posts.
    """
    
    # Who commented
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    
    # Which post was commented on
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        related_name='comments'  # post.comments.all() = comments on this post
    )
    
    # The comment text
    content = models.TextField(
        max_length=500,
        help_text="Your comment (max 500 chars)"
    )
    
    # When the comment was made
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)  # For editing comments
    
    # Parent comment for replies (optional - for nested comments)
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='replies'
    )
    
    # Soft delete
    is_deleted = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['created_at']  # Oldest comments first (or -created_at for newest)
        verbose_name = 'Comment'
        verbose_name_plural = 'Comments'
    
    def __str__(self):
        return f"{self.user.username}: {self.content[:30]}..."
    
    @property
    def replies_count(self):
        """Count of replies to this comment"""
        return self.replies.count()
    
    def delete(self, *args, **kwargs):
        """Soft delete - mark as deleted instead of removing"""
        self.is_deleted = True
        self.save()