from rest_framework import serializers
from .models import Post,Follow
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