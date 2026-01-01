# API Endpoints Overview

# Register User
POST /accounts/register/
Request Body:
{
    "username": "john_doe",
    "email": "john@example.com",
    "password": "securepassword123",
    "password2": "securepassword123",
    "bio": "Software developer from NYC",
    "profile_picture": "https://example.com/profile.jpg"
}

Required Fields: username, email, password, password2

Response:
{
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "bio": "Software developer from NYC",
        "profile_picture": "https://example.com/profile.jpg",
        "followers_count": 0,
        "following_count": 0,
        "posts_count": 0,
        "date_joined": "2024-01-01T12:00:00Z"
    },
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
    "message": "User created successfully!"
}

# Login User
POST /accounts/login/
Request Body:
{
    "username": "john_doe",
    "password": "securepassword123"
}

Response:
{
    "user": {
        "id": 1,
        "username": "john_doe",
        "email": "john@example.com",
        "bio": "Software developer from NYC",
        "profile_picture": "https://example.com/profile.jpg",
        "followers_count": 5,
        "following_count": 3,
        "posts_count": 12,
        "date_joined": "2024-01-01T12:00:00Z"
    },
    "refresh": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
    "access": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...",
    "message": "Login successful!"
}


# Get Current User Profile
GET /accounts/me/
Headers:
Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1...

Response:
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "bio": "Software developer from NYC",
    "profile_picture": "https://example.com/profile.jpg",
    "followers_count": 5,
    "following_count": 3,
    "posts_count": 12,
    "is_following": false,
    "follows_you": false,
    "date_joined": "2024-01-01T12:00:00Z",
    "last_login": "2024-01-15T10:30:00Z"
}


# Update User Profile
PUT /accounts/me/
Headers:
Authorization: Bearer <token>
Content-Type: application/json

Request Body (partial update allowed):
{
    "bio": "Updated bio - Full Stack Developer",
    "profile_picture": "https://example.com/new-profile.jpg"
}

Response:
{
    "id": 1,
    "username": "john_doe",
    "email": "john@example.com",
    "bio": "Updated bio - Full Stack Developer",
    "profile_picture": "https://example.com/new-profile.jpg",
    "followers_count": 5,
    "following_count": 3,
    "posts_count": 12,
    "date_joined": "2024-01-01T12:00:00Z"
}


# User Management Endpoints
# List All Users
GET /accounts/users/

Query Parameters:

?search=john - Search by username

?page=1 - Page number (default: 1)

?page_size=10 - Items per page (default: 10)

Response (200 OK):
{
    "count": 150,
    "next": "http://127.0.0.1:8000/api/accounts/users/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "username": "john_doe",
            "profile_picture": "https://example.com/profile.jpg",
            "followers_count": 5,
            "following_count": 3,
            "is_following": false,
            "follows_you": false
        },
        {
            "id": 2,
            "username": "jane_smith",
            "profile_picture": "",
            "followers_count": 120,
            "following_count": 85,
            "is_following": true,
            "follows_you": false
        }
    ]
}


# Get Specific User
GET /accounts/users/{username}/

Example: GET /accounts/users/john_doe/

Response (200 OK):
{
    "id": 1,
    "username": "john_doe",
    "bio": "Software developer from NYC",
    "profile_picture": "https://example.com/profile.jpg",
    "followers_count": 5,
    "following_count": 3,
    "posts_count": 12,
    "is_following": true,
    "follows_you": false,
    "date_joined": "2024-01-01T12:00:00Z"
}


#  Post Endpoints
# Create Post
POST /posts/

Headers:
Authorization: Bearer <token>
Content-Type: application/json

Request Body:
{
    "content": "Just finished my Django project! #coding #django",
    "image": "https://example.com/project-screenshot.jpg"
}

Response:
{
    "id": 1,
    "user": {
        "id": 1,
        "username": "john_doe",
        "profile_picture": "https://example.com/profile.jpg"
    },
    "content": "Just finished my Django project! #coding #django",
    "image": "https://example.com/project-screenshot.jpg",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "likes_count": 0,
    "comments_count": 0,
    "is_liked": false,
    "recent_comments": []
}


# List All Posts
GET /posts/

Query Parameters:

?page=1 - Page number

?page_size=10 - Posts per page

?search=django - Search in content

?ordering=-created_at - Sort by newest first

?user=john_doe - Filter by user

Response (200 OK):
{
    "count": 45,
    "next": "http://127.0.0.1:8000/api/posts/?page=2",
    "previous": null,
    "results": [
        {
            "id": 1,
            "user": {
                "id": 1,
                "username": "john_doe",
                "profile_picture": "https://example.com/profile.jpg"
            },
            "content": "Just finished my Django project!",
            "image": "https://example.com/image.jpg",
            "created_at": "2024-01-15T10:30:00Z",
            "likes_count": 5,
            "comments_count": 2,
            "is_liked": true
        }
    ]
}


# Get Specific Post
GET /posts/{id}/

Example: GET /posts/1/

Response (200 OK):
{
    "id": 1,
    "user": {
        "id": 1,
        "username": "john_doe",
        "profile_picture": "https://example.com/profile.jpg"
    },
    "content": "Just finished my Django project!",
    "image": "https://example.com/image.jpg",
    "created_at": "2024-01-15T10:30:00Z",
    "updated_at": "2024-01-15T10:30:00Z",
    "likes_count": 5,
    "comments_count": 2,
    "is_liked": true,
    "recent_comments": [
        {
            "id": 1,
            "user": {
                "id": 2,
                "username": "jane_smith",
                "profile_picture": ""
            },
            "content": "Great work!",
            "created_at": "2024-01-15T10:35:00Z"
        }
    ]
}


# Update Post
PUT /posts/{id}/

Headers:
Authorization: Bearer <token>
Content-Type: application/json

Request Body:
{
    "content": "Updated: Just finished my Django project with React frontend!",
    "image": "https://example.com/new-screenshot.jpg"
}

Response (200 OK): Updated post object


# Delete Post
DELETE /posts/{id}/

Headers:
Authorization: Bearer <token>

Response (200 OK):
{
    "message": "Post deleted successfully."
}


#  Get User's Posts
GET /posts/user/{username}/

Example: GET /posts/user/john_doe/

Response (200 OK): List of user's posts


# Feed Endpoints
13. Personalized Feed
GET /feed/

Shows posts from users you follow + your own posts.

Query Parameters:

?page=1 - Page number

?page_size=10 - Posts per page

?date_from=2024-01-01 - Filter from date

?date_to=2024-01-31 - Filter to date

?search=project - Search in content

Response (200 OK):
{
    "feed_info": {
        "user": "john_doe",
        "following_count": 3,
        "posts_in_feed": 25
    },
    "pagination": {
        "count": 25,
        "page_size": 10,
        "total_pages": 3,
        "current_page": 1,
        "next_page": 2,
        "previous_page": null,
        "has_next": true,
        "has_previous": false
    },
    "posts": [
        {
            "id": 1,
            "user": {
                "id": 2,
                "username": "jane_smith",
                "profile_picture": ""
            },
            "content": "Working on a new React project!",
            "created_at": "2024-01-15T09:00:00Z",
            "likes_count": 8,
            "comments_count": 3,
            "is_liked": false
        }
    ]
}



# Global Feed
GET /feed/global/

Shows all posts from all users.

Response (200 OK): Similar to personalized feed



# Follow System Endpoints
# Follow User
POST /follow/follow/

Headers:
Authorization: Bearer <token>
Content-Type: application/json

Request Body:
{
    "username": "jane_smith"
}

Response (201 Created):
{
    "id": 1,
    "follower": {
        "id": 1,
        "username": "john_doe",
        "profile_picture": "https://example.com/profile.jpg"
    },
    "following": {
        "id": 2,
        "username": "jane_smith",
        "profile_picture": ""
    },
    "created_at": "2024-01-15T10:40:00Z"
}


# Unfollow User
POST /follow/unfollow/

Request Body:
{
    "username": "jane_smith"
}

Response (200 OK):
{
    "message": "You have unfollowed jane_smith."
}


# Get Followers
GET /follow/followers/

Response (200 OK):
[
    {
        "id": 3,
        "username": "bob_johnson",
        "profile_picture": "",
        "followers_count": 2,
        "following_count": 5,
        "is_following": true,
        "follows_you": true
    }
]


# Get Following
GET /follow/following/

Response (200 OK): List of users you follow
Like Endpoints


# Like a Post
POST /posts/{id}/likes/

Example: POST /posts/1/likes/

Response (201 Created):
{
    "id": 1,
    "user": {
        "id": 1,
        "username": "john_doe",
        "profile_picture": "https://example.com/profile.jpg"
    },
    "created_at": "2024-01-15T10:45:00Z"
}


# Unlike a Post
DELETE /posts/{id}/unlike/

Response (200 OK):

{
    "message": "Post unliked successfully."
}


# Get Post Likes
GET /posts/{id}/likes/

Response (200 OK):

[
    {
        "id": 1,
        "user": {
            "id": 1,
            "username": "john_doe",
            "profile_picture": "https://example.com/profile.jpg"
        },
        "created_at": "2024-01-15T10:45:00Z"
    }
]

# Comment Endpoints
# Add Comment
POST /posts/{id}/comments/

Headers:
Authorization: Bearer <token>
Content-Type: application/json
Request Body:
{
    "content": "This is amazing work! How long did it take?"
}

Response (201 Created):
{
    "id": 1,
    "user": {
        "id": 1,
        "username": "john_doe",
        "profile_picture": "https://example.com/profile.jpg"
    },
    "content": "This is amazing work! How long did it take?",
    "created_at": "2024-01-15T10:50:00Z",
    "updated_at": "2024-01-15T10:50:00Z",
    "replies_count": 0,
    "replies": []
}


# Get Post Comments
GET /posts/{id}/comments/

Response (200 OK):
[
    {
        "id": 1,
        "user": {
            "id": 1,
            "username": "john_doe",
            "profile_picture": "https://example.com/profile.jpg"
        },
        "content": "Great post!",
        "created_at": "2024-01-15T10:50:00Z",
        "replies_count": 1,
        "replies": [
            {
                "id": 2,
                "user": {
                    "id": 2,
                    "username": "jane_smith",
                    "profile_picture": ""
                },
                "content": "Thanks!",
                "created_at": "2024-01-15T10:55:00Z",
                "replies_count": 0,
                "replies": []
            }
        ]
    }
]

# Update Comment
PUT /comments/{id}/
Request Body:
{
    "content": "Updated comment text"
}


# Delete Comment
DELETE /comments/{id}/
Response (200 OK):
json
{
    "message": "Comment deleted successfully."
}


# Reply to Comment
POST /comments/{id}/reply/
Request Body:
{
    "content": "I agree with you!"
}

 Error Responses
400 Bad Request
{
    "error": "Validation error",
    "details": {
        "username": ["This field is required."],
        "password": ["Password must be at least 8 characters."]
    }
}

401 Unauthorized
{
    "detail": "Authentication credentials were not provided."
}

403 Forbidden
{
    "detail": "You do not have permission to perform this action."
}

404 Not Found
{
    "detail": "Not found."
}

409 Conflict
{
    "error": "You are already following this user."
}


# Health Check
# API Health
GET /health/
Response (200 OK):
{
    "status": "healthy",
    "timestamp": "2024-01-15T11:00:00Z",
    "service": "Social Media API",
    "version": "1.0.0",
    "checks": {
        "database": {
            "status": "connected",
            "message": "PostgreSQL database is connected"
        },
        "application": {
            "status": "running",
            "endpoints": {
                "api_root": "/api/",
                "docs": "/api/docs/",
                "register": "/api/accounts/register/",
                "feed": "/api/feed/"
            }
        }
    }
}
