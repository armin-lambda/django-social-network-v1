from datetime import timedelta
import random
import os

from django.contrib import messages
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Q, Count
from django.utils import timezone

from notifications.models import Notification
from utils.pagination import get_pagination_context
from utils.base import send_otp_code
from utils.mixins import (
    AnonymousRequiredMixin,
    OwnerRequiredMixin,
    SelfForbiddenMixin,
)
from .models import Relation, Story
from .forms import (
    RegisterForm,
    LoginForm,
    ResetPasswordForm,
    AccountEditForm,
    AccountDeleteForm,
    StoryCreateForm,
)


User = get_user_model()


class PeopleView(LoginRequiredMixin, View):
    template_name = 'accounts/people.html'

    def get(self, request):
        # users = User.objects.all()
        users = User.objects.annotate(
            followers_count=Count('followers'),
        ).order_by('-followers_count')

        if request.GET.get('search'):
            search = request.GET['search']
            users = users.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(bio__icontains=search)
            )

        return render(request, self.template_name, {
            'page_obj': get_pagination_context(request, users, 10),
        })


class RegisterView(AnonymousRequiredMixin, View):
    template_name = 'accounts/register.html'
    form_class = RegisterForm

    def get(self, request):
        return render(request, self.template_name, {
            'form': self.form_class(),
        })
    
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            user = User.objects.create_user(
                username=cd['username'],
                email=cd['email'],
                password=cd['password']
            )
            user.first_name = cd['first_name']
            user.last_name = cd['last_name']
            user.phone_number = cd['phone_number']
            user.save()
            messages.success(request, 'Successfully registered', 'info')
            return redirect('accounts:login')
        return render(request, self.template_name, {
            'form': form,
        })


class LoginView(AnonymousRequiredMixin, View):
    template_name = 'accounts/login.html'
    form_class = LoginForm

    def get(self, request):
        return render(request, self.template_name, {
            'form': self.form_class(),
        })
    
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            user = authenticate(request, username=cd['username'], password=cd['password'])

            if user is not None:
                login(request, user)
                messages.success(request, 'Successfully logged in', 'info')
                return redirect(request.GET.get('next') or 'social_network')
            messages.error(request, 'Incorrect Username or Password', 'danger')
            return redirect('accounts:login')
        return render(request, self.template_name, {
            'form': form,
        })


class LogoutView(LoginRequiredMixin, View):
    def get(self, request):
        logout(request)
        messages.success(request, 'Successfully logged out', 'info')
        return redirect('social_network')


# ---- RESET PASSWORD ----

class SendOTPCodeView(AnonymousRequiredMixin, View):
    template_name = 'accounts/send_otp_code.html'

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        phone_number = request.POST.get('phone_number')

        if User.objects.filter(phone_number=phone_number).exists():
            """
            Send otp_code to the phone_number.
            """
            otp_code = str(random.randint(1000, 9999))
            send_otp_code(phone_number, otp_code)

            # Just in Dev.
            print(f"\n\n{phone_number} - {otp_code}\n\n")
            
            request.session['phone_number'] = phone_number
            request.session['otp_code'] = otp_code

            messages.success(request, 'We sent you a code', 'info')
            return redirect('accounts:verify_otp_code')
        messages.error(request, 'There is no user with this phone number', 'danger')
        return redirect('accounts:send_otp_code')


class VerifyOTPCodeView(AnonymousRequiredMixin, View):
    template_name = 'accounts/verify_otp_code.html'

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('otp_code'):
            return redirect('accounts:send_otp_code')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name)
    
    def post(self, request):
        input_otp_code = request.POST.get('otp_code')
        real_otp_code = request.session.get('otp_code')

        if input_otp_code == real_otp_code:
            request.session['otp_code_verified'] = True
            messages.success(request, 'The code verified', 'info')
            return redirect('accounts:reset_password')
        messages.error(request, 'Incorrect Code', 'danger')
        return redirect('accounts:verify_otp_code')


class ResetPasswordView(AnonymousRequiredMixin, View):
    template_name = 'accounts/reset_password.html'
    form_class = ResetPasswordForm

    def dispatch(self, request, *args, **kwargs):
        if not request.session.get('otp_code_verified'):
            return redirect('accounts:verify_otp_code')
        return super().dispatch(request, *args, **kwargs)

    def get(self, request):
        return render(request, self.template_name, {
            'form': self.form_class(),
        })
    
    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            phone_number = request.session.get('phone_number')

            user = get_object_or_404(User, phone_number=phone_number)
            user.set_password(cd['password'])
            user.save()

            del request.session['phone_number']
            del request.session['otp_code']
            del request.session['otp_code_verified']

            messages.success(request, 'Successfully changed password', 'info')
            return redirect('accounts:login')
        return render(request, self.template_name, {
            'form': form,
        })

# ---- END RESET PASSWORD ----


class ProfileView(LoginRequiredMixin, View):
    template_name = 'accounts/profile.html'

    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        stories = user.stories.filter(
            created_at__gte = timezone.now() - timedelta(hours=24)
        )
        is_followed = Relation.objects.filter(from_user=request.user, to_user=user).exists()
        return render(request, self.template_name, {
            'user': user,
            'stories': stories,
            'is_followed': is_followed,
        })


class AccountEditView(LoginRequiredMixin, OwnerRequiredMixin, View):
    template_name = 'accounts/account_edit.html'
    form_class = AccountEditForm

    def setup(self, request, *args, **kwargs):
        self.user_instance = get_object_or_404(User, username=kwargs['username'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, **kwargs):
        user = self.user_instance
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
    
    def post(self, request, **kwargs):
        form = self.form_class(request.POST, request.FILES)

        if form.is_valid():
            cd = form.cleaned_data
            user = self.user_instance

            if User.objects.filter(username=cd['username']).exclude(username=user.username).exists():
                form.add_error('username', 'This username already exists')
            elif User.objects.filter(email=cd['email']).exclude(email=user.email).exists():
                form.add_error('email', 'This email address already exists')
            elif User.objects.filter(phone_number=cd['phone_number']).exclude(phone_number=cd['phone_number']).exists():
                form.add_error('phone_number', 'This phone number already exists.')
            else:
                user.username = cd['username']
                user.email = cd['email']
                user.first_name = cd['first_name']
                user.last_name = cd['last_name']
                user.phone_number = cd['phone_number']
                user.bio = cd['bio']
                user.website_url = cd['website_url']

                if cd['image'] is not None:
                    if user.image:
                        os.remove(user.image.path)
                        user.image.delete()
                    user.image = cd['image']

                user.save()
                messages.success(request, 'Successfully edited account', 'info')
                return redirect(user.get_profile_url())
            return render(request, self.template_name, {
                'form': form,
            })


class ProfileImageDeleteView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])

        if user.image:
            os.remove(user.image.path)
            user.image.delete()
            messages.success(request, 'Successfully deleted profile image', 'info')
        return redirect(user.get_profile_url())


class AccountDeleteView(LoginRequiredMixin, OwnerRequiredMixin, View):
    template_name = 'accounts/account_delete.html'
    form_class = AccountDeleteForm

    def get(self, request, **kwargs):
        return render(request, self.template_name, {
            'form': self.form_class(),
        })
    
    def post(self, request, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            cd = form.cleaned_data
            user = get_object_or_404(User, username=kwargs['username'])
            
            if user.username == cd['username']:
                user.delete()
                messages.success(request, 'Successfully deleted account', 'info')
                return redirect('social_network')
            form.add_error('username', 'Wrong username')
        return render(request, self.template_name, {
            'form': form,
        })


class FollowView(LoginRequiredMixin, SelfForbiddenMixin, View):
    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])

        if not Relation.objects.filter(from_user=request.user, to_user=user).exists():
            relation = Relation.objects.create(from_user=request.user, to_user=user)
            Notification.objects.create(
                from_user=request.user,
                to_user=user,
                notification_type='follow',
                relation=relation,
            )
            messages.success(request, f"Successfully followed `{user.username}`", 'info')
        return redirect(user.get_profile_url())


class UnfollowView(LoginRequiredMixin, SelfForbiddenMixin, View):
    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        relation = Relation.objects.filter(from_user=request.user, to_user=user)
        
        if relation.exists():
            relation.delete()
            messages.success(request, f"Successfully unfollowed `{user.username}`", 'info')
        return redirect(user.get_profile_url())


class FollowersView(LoginRequiredMixin, View):
    template_name = 'accounts/followers.html'

    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        followers = user.get_followers()

        if request.GET.get('search'):
            search = request.GET['search']
            followers = followers.filter(
                Q(username__contains=search) |
                Q(email__contains=search) |
                Q(first_name__contains=search) |
                Q(last_name__contains=search) |
                Q(bio__contains=search)
            )

        return render(request, self.template_name, {
            'user': user,
            'page_obj': get_pagination_context(request, followers, 10),
        })


class FollowingView(LoginRequiredMixin, View):
    template_name = 'accounts/following.html'

    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        following = user.get_following()

        if request.GET.get('search'):
            search = request.GET['search']
            following = following.filter(
                Q(username__icontains=search) |
                Q(email__icontains=search) |
                Q(first_name__icontains=search) |
                Q(last_name__icontains=search) |
                Q(bio__icontains=search)
            )

        return render(request, self.template_name, {
            'user': user,
            'page_obj': get_pagination_context(request, following, 10),
        })


class PostsView(LoginRequiredMixin, View):
    template_name = 'accounts/posts.html'

    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        # posts = user.posts.all()
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


class SavedPostsView(LoginRequiredMixin, OwnerRequiredMixin, View):
    template_name = 'accounts/saved_posts.html'

    def get(self, request, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        posts = user.get_saved_posts()
        
        if request.GET.get('search'):
            search = request.GET['search']
            posts = posts.filter(body__icontains=search)

        return render(request, self.template_name, {
            'user': user,
            'page_obj': get_pagination_context(request, posts, 10),
        })


class StoryCreateView(LoginRequiredMixin, OwnerRequiredMixin, View):
    template_name = 'accounts/story_create.html'
    form_class = StoryCreateForm

    def get(self, request, **kwargs):
        return render(request, self.template_name, {
            'form': self.form_class(),
        })

    def post(self, request, **kwargs):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = get_object_or_404(User, username=kwargs['username'])
            story = form.save(commit=False)
            story.user = user
            story.save()

            followers = user.get_followers()
            
            notifications = [
                Notification(
                    from_user=user,
                    to_user=f,
                    notification_type='story',
                    story=story,
                )
                for f in followers
            ]

            Notification.objects.bulk_create(notifications)

            messages.success(request, 'Successfully created story', 'info')
            return redirect(user.get_profile_url())
        return render(request, self.template_name, {
            'form': form,
        })


class StoryDeleteView(LoginRequiredMixin, OwnerRequiredMixin, View):
    def get(self, request, **kwargs):
        get_object_or_404(Story, user=request.user, pk=kwargs['pk']).delete()
        messages.success(request, 'Successfully deleted story', 'info')
        return redirect(request.user.get_profile_url())