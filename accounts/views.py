import random
import os

from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Q, Count
from django.contrib import messages
from django.contrib.auth import login, logout, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType

from notifications.models import Notification
from utils.pagination import get_pagination_context
from utils.base import send_sms
from utils.mixins import AnonymousRequiredMixin, SelfForbiddenMixin
from .models import Relation, Story, GalleryImage
from .forms import (
    UserCreateForm,
    UserLoginForm,
    UserPasswordResetForm,
    UserPasswordVerifyCodeForm,
    UserPasswordChangeForm,
    UserUpdateForm,
    UserDeleteForm,
    UserStoryCreateForm,
    UserGalleryImageCreateForm,
)


User = get_user_model()


class UserCreateView(AnonymousRequiredMixin, View):
    template_name = 'accounts/user_create.html'
    form_class = UserCreateForm

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class()})
    
    def post(self, request):
        form = self.form_class(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})
        
        form.save()
        messages.success(request, 'Registered successfully', 'success')
        return redirect('accounts:user-login')


class UserLoginView(AnonymousRequiredMixin, View):
    template_name = 'accounts/user_login.html'
    form_class = UserLoginForm

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class()})
    
    def post(self, request):
        form = self.form_class(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})
        
        user = form.user
        login(request, user)
        messages.success(request, 'Logged in successfully', 'success')
        return redirect(request.GET.get('next') or 'social_network')


class UserLogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Logged out successfully', 'success')
        return redirect('social_network')


# ---- RESET PASSWORD ----

class UserPasswordResetView(AnonymousRequiredMixin, View):
    template_name = 'accounts/user_password_reset.html'
    form_class = UserPasswordResetForm

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class()})
    
    def post(self, request):
        form = self.form_class(request.POST)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})
        
        user = form.save()
        otp_code = random.randint(1000, 9999)

        request.session['user_info'] = {
            'username': user.username,
            'phone_number': str(user.phone_number),
            'otp_code': otp_code,
        }

        send_sms(user.phone_number, otp_code)
        messages.success(request, 'We sent you a code', 'success')
        return redirect('accounts:user-password-verify-code')


class UserPasswordVerifyCodeView(AnonymousRequiredMixin, View):
    template_name = 'accounts/user_password_verify_code.html'
    form_class = UserPasswordVerifyCodeForm

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('user_info'):
            return redirect('accounts:user-password-reset')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class()})
    
    def post(self, request):
        form = self.form_class(request.POST, otp_code=request.session['user_info']['otp_code'])

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})
        
        request.session['code_verified'] = True
        messages.success(request, 'That code verified successfully', 'success')
        return redirect('accounts:user-password-change')


class UserPasswordChangeView(AnonymousRequiredMixin, View):
    template_name = 'accounts/user_password_change.html'
    form_class = UserPasswordChangeForm

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('code_verified'):
            return redirect('accounts:user-password-verify-code')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class()})
    
    def post(self, request):
        form = self.form_class(request.POST, username=request.session['user_info']['username'])

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})
        
        form.save()

        del request.session['user_info']
        del request.session['code_verified']

        messages.success(request, 'Password changed successfully', 'success')
        return redirect('accounts:user-login')

# ---- END RESET PASSWORD ----


class UserListView(LoginRequiredMixin, View):
    template_name = 'accounts/user_list.html'

    def get(self, request):
        user_list = User.objects.annotate(
            followers_count=Count('followers'),
        ).order_by('-followers_count')

        if request.GET.get('search'):
            search = request.GET['search']
            user_list = user_list.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(bio__icontains=search)
            )

        return render(request, self.template_name, {
            'page_obj': get_pagination_context(request, user_list, 10),
        })


class UserUpdateView(LoginRequiredMixin, View):
    template_name = 'accounts/user_update.html'
    form_class = UserUpdateForm

    def get(self, request):
        user = request.user
        return render(request, self.template_name, {
            'form': self.form_class(initial={
                'username': user.username,
                'email': user.email,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': user.phone_number,
                'bio': user.bio,
                'website_url': user.website_url,
            }),
        })
    
    def post(self, request):
        form = self.form_class(request.POST, request.FILES, user=request.user)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        form.save()
        messages.success(request, 'Profile edited successfully', 'success')
        return redirect(request.user.get_absolute_url())


class UserDeleteView(LoginRequiredMixin, View):
    template_name = 'accounts/user_delete.html'
    form_class = UserDeleteForm

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class()})
    
    def post(self, request):
        form = self.form_class(request.POST, user=request.user)
        
        if not form.is_valid():
            return render(request, self.template_name, {'form': form})
        
        form.save()
        messages.success(request, 'Account deleted successfully', 'success')
        return redirect('social_network')


class UserProfileImageDeleteView(LoginRequiredMixin, View):
    def get(self, request):
        user = request.user

        if user.image and user.image.path:
            os.remove(user.image.path)
            user.image.delete()
            messages.success(request, 'Profile image deleted successfully', 'success')
        return redirect(user.get_absolute_url())


class UserStoryCreateView(LoginRequiredMixin, View):
    template_name = 'accounts/user_story_create.html'
    form_class = UserStoryCreateForm

    def dispatch(self, request, *args, **kwargs):
        if request.user.get_stories_count() >= 24:
            return redirect(request.user.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST, user=request.user)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})

        story = form.save()
        notifications = [
            Notification(
                from_user=story.user,
                to_user=f,
                type=Notification.Type.STORY,
                content_type=ContentType.objects.get_for_model(Story),
                object_id=story.id,
            )
            for f in story.user.get_follower_list()
        ]
        Notification.objects.bulk_create(notifications)

        messages.success(request, 'Story created successfully.', 'success')
        return redirect(request.user.get_absolute_url())


class UserStoryDeleteView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        get_object_or_404(Story, user=request.user, pk=kwargs['pk']).delete()
        messages.success(request, 'Story deleted successfully', 'success')
        return redirect(request.user.get_absolute_url())


class UserGalleryImageCreateView(LoginRequiredMixin, View):
    template_name = 'accounts/user_gallery_image_create.html'
    form_class = UserGalleryImageCreateForm
    
    def dispatch(self, request, *args, **kwargs):
        if request.user.get_gallery_images_count() >= 9:
            return redirect(request.user.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class()})
    
    def post(self, request):
        form = self.form_class(request.POST, request.FILES, user=request.user)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})
        
        form.save()
        messages.success(request, 'That image added to gallery successfully', 'success')
        return redirect(request.user.get_absolute_url())


class UserGalleryImageDeleteView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        user = request.user
        image = get_object_or_404(GalleryImage, user=user, pk=kwargs['pk'])

        if image.file.path:
            os.remove(image.file.path)
            image.delete()
            messages.success(request, 'Gallery image deleted successfully', 'success')
        return redirect(user.get_absolute_url())


class UserSavedPostListView(LoginRequiredMixin, View):
    template_name = 'accounts/user_saved_post_list.html'

    def get(self, request):
        user = request.user
        posts = user.get_saved_post_list()
        
        if request.GET.get('search'):
            search = request.GET['search']
            posts = posts.filter(body__icontains=search)

        return render(request, self.template_name, {
            'user': user,
            'page_obj': get_pagination_context(request, posts, 10),
        })


class UserDetailView(LoginRequiredMixin, View):
    template_name = 'accounts/user_detail.html'

    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        return render(request, self.template_name, {
            'user': user,
            'story_list': user.get_story_list(),
            'is_followed': Relation.objects.filter(from_user=request.user, to_user=user).exists(),
        })


class UserFollowView(LoginRequiredMixin, SelfForbiddenMixin, View):
    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])

        if not Relation.objects.filter(from_user=request.user, to_user=user).exists():
            relation = Relation.objects.create(from_user=request.user, to_user=user)
            Notification.objects.create(
                from_user=request.user,
                to_user=user,
                type=Notification.Type.FOLLOW,
                content_type=ContentType.objects.get_for_model(Relation),
                object_id=relation.id,
            )
            messages.success(request, 'Followed successfully', 'success')
        return redirect(user.get_absolute_url())


class UserUnfollowView(LoginRequiredMixin, SelfForbiddenMixin, View):
    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        
        if relation.exists():
            relation.delete()
            messages.success(request, 'Unfollowed successfully', 'success')
        return redirect(user.get_absolute_url())


class UserFollowerListView(LoginRequiredMixin, View):
    template_name = 'accounts/user_follower_list.html'

    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        follower_list = user.get_follower_list()

        if request.GET.get('search'):
            search = request.GET['search']
            follower_list = follower_list.filter(
                Q(username__contains=search) |
                Q(email__contains=search) |
                Q(first_name__contains=search) |
                Q(last_name__contains=search) |
                Q(bio__contains=search)
            )

        return render(request, self.template_name, {
            'user': user,
            'page_obj': get_pagination_context(request, follower_list, 10),
        })


class UserFollowingListView(LoginRequiredMixin, View):
    template_name = 'accounts/user_following_list.html'

    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        following_list = user.get_following_list()

        if request.GET.get('search'):
            search = request.GET['search']
            following_list = following_list.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(bio__icontains=search)
            )

        return render(request, self.template_name, {
            'user': user,
            'page_obj': get_pagination_context(request, following_list, 10),
        })


class UserPostListView(LoginRequiredMixin, View):
    template_name = 'accounts/user_post_list.html'

    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        posts = user.posts.annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments'),
        ).order_by('-likes_count', '-comments_count', '-created_at')

        if request.GET.get('search'):
            search = request.GET['search']
            posts = posts.filter(body__icontains=search)

        return render(request, self.template_name, {
            'user': user,
            'page_obj': get_pagination_context(request, posts, 10),
        })
