from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

@admin.register(User)
class CustomUserAdmin(UserAdmin):
    """Customize how users appear in admin panel"""
    
    # Fields to show in list view
    list_display = ('username', 'email', 'is_staff', 'created_at')
    
    # Fields to show when editing
    fieldsets = UserAdmin.fieldsets + (
        ('Extra Info', {'fields': ('bio', 'profile_picture')}),
    )