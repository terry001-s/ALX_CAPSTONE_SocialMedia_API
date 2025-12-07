from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()  # Gets our custom User model

class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    # Read-only fields (can't be modified through API)
    followers_count = serializers.IntegerField(read_only=True)
    following_count = serializers.IntegerField(read_only=True)
    
    class Meta:
        model = User
        fields = [
            'id',
            'username',
            'email',
            'bio',
            'profile_picture',
            'followers_count',
            'following_count',
            'date_joined',
        ]
        # Extra settings
        extra_kwargs = {
            'email': {'required': True},
            'password': {'write_only': True, 'required': True},
        }
    
    def create(self, validated_data):
        """Create a new user with encrypted password"""
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        return user