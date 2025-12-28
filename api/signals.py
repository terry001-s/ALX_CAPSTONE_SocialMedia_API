from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Follow, Like, Comment, Notification

@receiver(post_save, sender=Follow)
def create_follow_notification(sender, instance, created, **kwargs):
    """Create notification when someone follows you"""
    if created:
        Notification.objects.create(
            user=instance.following,
            type='follow',
            message=f"{instance.follower.username} started following you",
            related_user=instance.follower
        )

@receiver(post_save, sender=Like)
def create_like_notification(sender, instance, created, **kwargs):
    """Create notification when someone likes your post"""
    if created and instance.user != instance.post.user:  # Don't notify for self-likes
        Notification.objects.create(
            user=instance.post.user,
            type='like',
            message=f"{instance.user.username} liked your post",
            related_user=instance.user,
            related_post=instance.post
        )

@receiver(post_save, sender=Comment)
def create_comment_notification(sender, instance, created, **kwargs):
    """Create notification when someone comments on your post"""
    if created and instance.user != instance.post.user:  # Don't notify for self-comments
        Notification.objects.create(
            user=instance.post.user,
            type='comment',
            message=f"{instance.user.username} commented on your post",
            related_user=instance.user,
            related_post=instance.post,
            related_comment=instance
        )