from django.db import models
from django.conf import settings
from django.urls import reverse


User = settings.AUTH_USER_MODEL


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    body = models.TextField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.get_short_body()
    
    def get_short_body(self):
        return (self.body[:20] + '...') if len(self.body) > 20 else self.body

    # ----- URLS -----
    def get_absolute_url(self):
        return reverse('posts:post-detail', args=[self.pk])

    def get_update_url(self):
        return reverse('posts:post-update', args=[self.pk])

    def get_delete_url(self):
        return reverse('posts:post-delete', args=[self.pk])
    
    def get_like_url(self):
        return reverse('posts:post-like', args=[self.pk])
    
    def get_unlike_url(self):
        return reverse('posts:post-unlike', args=[self.pk])
    
    def get_save_url(self):
        return reverse('posts:post-save', args=[self.pk])
    
    def get_unsave_url(self):
        return reverse('posts:post-unsave', args=[self.pk])
    
    # ----- COUNTS -----
    def get_likes_count(self):
        return self.likes.count()
    
    def get_comments_count(self):
        return self.comments.count()
    
    def get_saves_count(self):
        return self.saves.count()
    
    # ----- LISTS -----
    def get_comment_list(self):
        return self.comments.all()


class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    body = models.TextField(max_length=5000)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return (self.body + '...') if len(self.body) > 20 else self.body


class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='liked_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user} liked {self.post}"


class Save(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_posts')
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='saves')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['user', 'post']
    
    def __str__(self):
        return f"{self.user.username} saved {self.post.get_short_body()}"
