from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.contrib.auth import authenticate
from django.core.exceptions import ValidationError
from api.serializers import UserDetailSerializer

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
    

class RegisterSerializer(serializers.ModelSerializer):
    """Serializer for user registration"""
    
    password = serializers.CharField(write_only=True, min_length=8)
    password2 = serializers.CharField(write_only=True, min_length=8)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password', 'password2', 'bio']
        extra_kwargs = {
            'email': {'required': True},
            'bio': {'required': False}
        }
    
    def validate(self, data):
        """Check that passwords match"""
        if data['password'] != data['password2']:
            raise serializers.ValidationError({"password": "Passwords must match."})
        return data
    
    def create(self, validated_data):
        """Create user with encrypted password"""
        # Remove password2 from validated data
        validated_data.pop('password2')
        
        # Create user
        user = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password']
        )
        
        # Add bio if provided
        if 'bio' in validated_data:
            user.bio = validated_data['bio']
            user.save()
        
        return user


class LoginSerializer(serializers.Serializer):
    """Serializer for user login"""
    
    username = serializers.CharField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, data):
        """Validate user credentials"""
        username = data.get('username')
        password = data.get('password')
        
        if username and password:
            # Try to authenticate user
            user = authenticate(username=username, password=password)
            
            if user:
                if not user.is_active:
                    raise serializers.ValidationError("User account is disabled.")
                data['user'] = user
            else:
                raise serializers.ValidationError("Unable to login with provided credentials.")
        else:
            raise serializers.ValidationError("Must include 'username' and 'password'.")
        
        return data


class UserProfileSerializer(UserDetailSerializer):
    """Serializer for user profile (with edit capabilities)"""
    
    class Meta(UserDetailSerializer.Meta):
        fields = UserDetailSerializer.Meta.fields
        read_only_fields = ['id', 'date_joined', 'followers_count', 
                          'following_count', 'posts_count', 'is_following', 'follows_you']
    
    def update(self, instance, validated_data):
        """Update user profile"""
        # Remove read-only fields if they somehow get in
        for field in ['followers_count', 'following_count', 'posts_count', 
                     'is_following', 'follows_you']:
            validated_data.pop(field, None)
        
        # Update user
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        return instance