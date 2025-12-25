from django.contrib import admin
from .models import Post,Follow,Like, Comment

@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    """Customize how posts appear in admin panel"""
    
    # Fields to show in list view
    list_display = ('id', 'user', 'content_preview', 'created_at', 'likes_count')
    
    # Add filters on the right
    list_filter = ('created_at', 'user')
    
    # Search functionality
    search_fields = ('content', 'user__username')
    
    # Make user clickable
    list_display_links = ('id', 'user')
    
    # Show newest first by default
    ordering = ('-created_at',)
    
    # Fields to show in detail/edit view
    fieldsets = (
        ('Post Information', {
            'fields': ('user', 'content', 'image')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)  # Hide by default
        }),
    )
    
    # Read-only fields (can't edit)
    readonly_fields = ('created_at', 'updated_at')
    
    def content_preview(self, obj):
        """Show first 50 chars of content"""
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Content Preview'
    
    def likes_count(self, obj):
        """Show likes count"""
        return obj.likes_count
    likes_count.short_description = 'Likes'

@admin.register(Follow)
class FollowAdmin(admin.ModelAdmin):
    """Admin interface for Follow relationships"""
    
    list_display = ('id', 'follower', 'following', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('follower__username', 'following__username')
    readonly_fields = ('created_at',)
    
    def get_queryset(self, request):
        """Optimize database queries"""
        return super().get_queryset(request).select_related('follower', 'following')
    

@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post_preview', 'created_at')
    list_filter = ('created_at',)
    search_fields = ('user__username', 'post__content')
    readonly_fields = ('created_at',)
    
    def post_preview(self, obj):
        return obj.post.content[:50] + "..." if len(obj.post.content) > 50 else obj.post.content
    post_preview.short_description = 'Post'

@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'post_preview', 'content_preview', 'created_at')
    list_filter = ('created_at', 'is_deleted')
    search_fields = ('user__username', 'content', 'post__content')
    readonly_fields = ('created_at', 'updated_at')
    
    def post_preview(self, obj):
        return f"Post #{obj.post.id}: {obj.post.content[:30]}..."
    post_preview.short_description = 'Post'
    
    def content_preview(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content
    content_preview.short_description = 'Comment'    