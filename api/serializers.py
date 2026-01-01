from rest_framework import serializers
from .models import Post,Follow, Like,Comment
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
    
    # Add these methods to PostSerializer:
    is_liked = serializers.SerializerMethodField()
    recent_comments = serializers.SerializerMethodField()
    
    class Meta:
        model = Post
        fields = [
            'id',
            'user',
            'user_id',
            'content',
            'image',
            'created_at',
            'updated_at',
            'likes_count',
            'comments_count',
            'is_liked',          # NEW: Check if current user liked this
            'recent_comments',   # NEW: Show recent comments
        ]
        read_only_fields = [
            'id', 'created_at', 'updated_at', 'user', 
            'likes_count', 'comments_count', 'is_liked', 'recent_comments'
        ]
    
    def get_is_liked(self, obj):
        """Check if current user liked this post"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.likes.filter(user=request.user).exists()
        return False
    
    def get_recent_comments(self, obj):
        """Get 3 most recent comments"""
        comments = obj.comments.filter(is_deleted=False).order_by('-created_at')[:3]
        return CommentSerializer(comments, many=True, read_only=True).data
    
    def validate_content(self, value):
        """Validate post content"""
        if len(value.strip()) == 0:
            raise serializers.ValidationError("Content cannot be empty.")
        if len(value) > 1000:
            raise serializers.ValidationError("Content too long (max 1000 chars).")
        return value.strip()
    
    def create(self, validated_data):
        """Create a new post"""
        # Get user from request context (this is already in validated_data via user_id)
        user = self.context['request'].user
    
        # Make sure the user from the request matches the user_id from the data
        # Or simply override with the request user for security
        validated_data['user'] = user
    
        # Create post
        post = Post.objects.create(**validated_data)
        return post
    
    def update(self, instance, validated_data):
        """Update an existing post"""
        # Users can only update content and image
        instance.content = validated_data.get('content', instance.content)
        instance.image = validated_data.get('image', instance.image)
        instance.save()
        return instance

class FollowSerializer(serializers.ModelSerializer):
    """Serializer for Follow relationships"""
    
    # Show user info instead of just IDs
    follower = UserBasicSerializer(read_only=True)
    following = UserBasicSerializer(read_only=True)
    
    # For creating follows: we need these as write-only fields
    follower_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='follower'
    )
    following_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(),
        write_only=True,
        source='following'
    )
    
    class Meta:
        model = Follow
        fields = [
            'id',
            'follower',      # Read-only user info
            'following',     # Read-only user info
            'follower_id',   # Write-only for creating
            'following_id',  # Write-only for creating
            'created_at',
        ]
        read_only_fields = ['id', 'created_at', 'follower', 'following']
    
    def validate(self, data):
        """Custom validation"""
        follower = data.get('follower') or self.context['request'].user
        following = data.get('following')
        
        # Check if trying to follow self
        if follower == following:
            raise serializers.ValidationError("You cannot follow yourself.")
        
        # Check if already following
        if Follow.objects.filter(follower=follower, following=following).exists():
            raise serializers.ValidationError("You are already following this user.")
        
        return data
    
    def create(self, validated_data):
        """Create follow relationship"""
        # Set follower to current user (from request)
        validated_data['follower'] = self.context['request'].user
        
        # Remove follower_id/following_id as we have actual objects
        validated_data.pop('follower_id', None)
        validated_data.pop('following_id', None)
        
        # Create follow
        return Follow.objects.create(**validated_data)


class UserDetailSerializer(serializers.ModelSerializer):
    """Enhanced user serializer with follow info"""
    
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    posts_count = serializers.IntegerField(read_only=True)
    
    # Check if current user follows this user
    is_following = serializers.SerializerMethodField()
    
    # Check if this user follows current user
    follows_you = serializers.SerializerMethodField()
    
    class Meta:
        model = User
        fields = [
            'id', 'username', 'email', 'bio', 'profile_picture',
            'followers_count', 'following_count', 'posts_count',
            'is_following', 'follows_you', 'date_joined'
        ]
        read_only_fields = fields
    
    def get_is_following(self, obj):
        """Check if current user follows this user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_followed_by(request.user)
        return False
    
    def get_follows_you(self, obj):
        """Check if this user follows current user"""
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            return obj.is_following(request.user)
        return False    
    

class LikeSerializer(serializers.ModelSerializer):
    """Serializer for Like model"""
    
    user = UserBasicSerializer(read_only=True)
    post_id = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(),
        write_only=True,
        source='post'
    )
    
    class Meta:
        model = Like
        fields = ['id', 'user', 'post_id', 'created_at']
        read_only_fields = ['id', 'user', 'created_at']
    
    def create(self, validated_data):
        """Create like - set user automatically"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    
    user = UserBasicSerializer(read_only=True)
    post_id = serializers.PrimaryKeyRelatedField(
        queryset=Post.objects.all(),
        write_only=True,
        source='post'
    )
    replies_count = serializers.IntegerField(read_only=True)
    
    # For nested comments/replies
    parent_id = serializers.PrimaryKeyRelatedField(
        queryset=Comment.objects.filter(is_deleted=False),
        write_only=True,
        source='parent',
        required=False,
        allow_null=True
    )
    
    # Nested replies (read-only)
    replies = serializers.SerializerMethodField()
    
    class Meta:
        model = Comment
        fields = [
            'id', 'user', 'post_id', 'parent_id',
            'content', 'created_at', 'updated_at',
            'replies_count', 'replies'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at', 'replies_count', 'replies']
    
    def get_replies(self, obj):
        """Get replies to this comment"""
        replies = obj.replies.filter(is_deleted=False).order_by('created_at')
        return CommentSerializer(replies, many=True, read_only=True).data
    
    def validate_content(self, value):
        """Validate comment content"""
        value = value.strip()
        if len(value) == 0:
            raise serializers.ValidationError("Comment cannot be empty.")
        if len(value) > 500:
            raise serializers.ValidationError("Comment too long (max 500 chars).")
        return value
    
    def create(self, validated_data):
        """Create comment - set user automatically"""
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data) 



class NotificationSerializer(serializers.Serializer):
    """Serializer for notifications"""
    id = serializers.IntegerField()
    type = serializers.CharField()
    message = serializers.CharField()
    is_read = serializers.BooleanField()
    created_at = serializers.DateTimeField()
    related_user = serializers.DictField(required=False)
    related_post_id = serializers.IntegerField(required=False)
    related_comment_id = serializers.IntegerField(required=False)
