from datetime import timedelta

from django.contrib.auth.models import AbstractUser
from django.core.validators import FileExtensionValidator
from django.conf import settings
from django.urls import reverse
from django.db import models
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

from posts.models import Post
from utils.paths import get_user_image_upload_path, get_gallery_image_upload_path
from utils.validators import UsernameValidator, NameValidator, URLValidator


User = settings.AUTH_USER_MODEL


class CustomUser(AbstractUser):
    username = models.CharField(
        max_length=30,
        unique=True,
        validators=[UsernameValidator()],
        error_messages={
            'unique': 'This username already exists.',
        },
    )
    email = models.EmailField(
        unique=True,
        verbose_name='email address',
        error_messages={
            'unique': 'This email address already exists.',
        },
    )
    first_name = models.CharField(
        max_length=15,
        validators=[NameValidator('First Name')],
    )
    last_name = models.CharField(
        max_length=15,
        validators=[NameValidator('Last Name')],
    )
    phone_number = PhoneNumberField(
        unique=True,
        error_messages={
            'unique': 'This phone number already exists.',
        },
    )
    bio = models.TextField(max_length=200, blank=True, null=True)
    image = models.ImageField(
        upload_to=get_user_image_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])],
    )
    website_url = models.URLField(
        max_length=100,
        blank=True,
        null=True,
        validators=[URLValidator()],
    )

    REQUIRED_FIELDS = ['email', 'first_name', 'last_name', 'phone_number']

    class Meta:
        ordering = ['username']
        verbose_name = 'User'
        verbose_name_plural = 'Users'

    # ----- URLS -----
    def get_absolute_url(self):
        return reverse('accounts:user-detail', args=[self.username])

    def get_update_url(self):
        return reverse('accounts:user-update')

    def get_profile_image_delete_url(self):
        return reverse('accounts:user-profile-image-delete')

    def get_delete_url(self):
        return reverse('accounts:user-delete')

    def get_follow_url(self):
        return reverse('accounts:user-follow', args=[self.username])

    def get_unfollow_url(self):
        return reverse('accounts:user-unfollow', args=[self.username])
    
    def get_gallery_image_create_url(self):
        return reverse('accounts:user-gallery-image-create')
    
    def get_following_list_url(self):
        return reverse('accounts:user-following-list', args=[self.username])
    
    def get_follower_list_url(self):
        return reverse('accounts:user-follower-list', args=[self.username])

    def get_post_create_url(self):
        return reverse('posts:post-create')
    
    def get_post_list_url(self):
        return reverse('accounts:user-post-list', args=[self.username])
    
    def get_saved_post_list_url(self):
        return reverse('accounts:user-saved-post-list')
    
    def get_story_create_url(self):
        return reverse('accounts:user-story-create')

    # ----- COUNTS -----
    def get_followers_count(self):
        return self.followers.count()

    def get_following_count(self):
        return self.following.count()
    
    def get_posts_count(self):
        return self.posts.count()
    
    def get_saved_posts_count(self):
        return self.saved_posts.count()
    
    def get_notifications_count(self):
        return self.notifications.filter(is_read=False).count()
    
    def get_stories_count(self):
        return self.stories.count()
    
    def get_gallery_images_count(self):
        return self.gallery_images.count()

    # ----- Lists -----
    def get_follower_list(self):
        return CustomUser.objects.filter(following__to_user=self)

    def get_following_list(self):
        return CustomUser.objects.filter(followers__from_user=self)
    
    def get_saved_post_list(self):
        return Post.objects.filter(saves__user=self)
    
    def get_gallery_image_list(self):
        return self.gallery_images.all()
    
    def get_story_list(self):
        expired_time = timezone.now() - timedelta(hours=24)
        return self.stories.filter(created_at__gte = expired_time)
    
    def get_notification_list(self):
        return self.notifications.all()


class Relation(models.Model):
    from_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='following')
    to_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='followers')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        unique_together = ['from_user', 'to_user']
    
    def __str__(self):
        return f'{self.from_user} followed {self.to_user}'


class Story(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='stories')
    content = models.TextField(max_length=120)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Story'
        verbose_name_plural = 'Stories'
    
    def __str__(self):
        return f"{self.user.username} - {self.get_short_content()}"

    def get_short_content(self):
        return (self.content[:20] + '...') if len(self.content) > 20 else self.content
    
    def get_delete_url(self):
        return reverse('accounts:user-story-delete', args=[self.pk])


class GalleryImage(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='gallery_images')
    file = models.ImageField(
        upload_to=get_gallery_image_upload_path,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])],  
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def get_delete_url(self):
        return reverse('accounts:user-gallery-image-delete', args=[self.pk])
