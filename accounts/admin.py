from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin

from .models import Relation, Story, GalleryImage
from .forms import CustomUserCreationForm, CustomUserChangeForm


User = get_user_model()


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    list_display = ['username', 'email', 'first_name', 'last_name', 'is_staff']
    list_filter = ['is_staff', 'is_superuser', 'is_active', 'groups']
    add_fieldsets = UserAdmin.add_fieldsets + (
        (
            'Personal Information', {
                'fields': (
                    'bio',
                    'image',
                    'website_url',
                )
            }
        ),
    )
    fieldsets = UserAdmin.fieldsets + (
        (
            'Personal Info', {
                'fields': (
                    'bio',
                    'image',
                    'website_url',
                )
            }
        ),
    )


@admin.register(Relation)
class RelationAdmin(admin.ModelAdmin):
    list_display = ['id', 'from_user', 'to_user', 'created_at']
    list_filter = ['from_user', 'to_user', 'created_at']
    search_fields = ['from_user__bio', 'to_user__bio']


@admin.register(Story)
class StoryAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']
    list_filter = ['user', 'created_at']
    search_fields = ['content']


@admin.register(GalleryImage)
class GalleryImageAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at']
    list_filter = ['user', 'created_at']