from django.contrib import admin
from .models import Post

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