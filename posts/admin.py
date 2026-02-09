from django.contrib import admin

from .models import Post, Comment, Like, Save


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'created_at', 'updated_at']
    list_filter = ['user', 'created_at', 'updated_at']
    search_fields = ['body']


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'created_at']
    list_filter = ['user', 'post', 'created_at']
    search_fields = ['body']


@admin.register(Like)
class LikeAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'created_at']
    list_filter = ['user', 'post', 'created_at']
    search_fields = ['user__username', 'post__body']


@admin.register(Save)
class SaveAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'post', 'created_at']
    list_filter = ['user', 'post', 'created_at']
    search_fields = ['body']
