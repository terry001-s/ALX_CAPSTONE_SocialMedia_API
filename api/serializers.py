from rest_framework import serializers
from .models import Post
from django.contrib.auth import get_user_model

User = get_user_model()

class UserBasicSerializer(serializers.ModelSerializer):
    """Simple user info for posts (to avoid circular imports)"""
    class Meta:
        model = User
        fields = ['id', 'username', 'profile_picture']


class PostSerializer(serializers.ModelSerializer):
    """Serializer for Post model"""
    
    # Include user info in posts
    user = UserBasicSerializer(read_only=True)  # Read-only, not set via API
    
    # Read-only counts (we'll implement likes/comments later)
    likes_count = serializers.IntegerField(read_only=True, default=0)
    comments_count = serializers.IntegerField(read_only=True, default=0)
    
    # For creating posts: we need user_id (set automatically from request)
    user_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,  # Only for input, not shown in response
        source='user'     # Map to 'user' field in model
    )
    
    class Meta:
        model = Post
        fields = [
            'id',
            'user',          # Read-only user info
            'user_id',       # Write-only for creating posts
            'content',
            'image',
            'created_at',
            'updated_at',
            'likes_count',
            'comments_count',
        ]
        read_only_fields = ['id', 'created_at', 'updated_at', 'user']
    
    def validate_content(self, value):
        """Validate post content"""
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Content cannot be empty.")
        if len(value) > 1000:
            raise serializers.ValidationError("Content too long (max 1000 chars).")
        return value.strip()
    
    def create(self, validated_data):
        """Create a new post"""
        # Remove user_id since we'll use request.user
        validated_data.pop('user_id', None)
        
        # Get user from request context
        user = self.context['request'].user
        
        # Create post
        post = Post.objects.create(user=user, **validated_data)
        return post
    
    def update(self, instance, validated_data):
        """Update an existing post"""
        # Users can only update content and image
        instance.content = validated_data.get('content', instance.content)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance