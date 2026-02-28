from django.contrib import messages
from django.contrib.auth import get_user_model
from django.shortcuts import redirect, get_object_or_404

from posts.models import Post


User = get_user_model()


class AnonymousRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, 'Access Denied', 'danger')
            return redirect('social_network')
        return super().dispatch(request, *args, **kwargs)


class OwnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        if request.user != user:
            messages.error(request, 'Access Denied', 'danger')
            return redirect('social_network')
        return super().dispatch(request, *args, **kwargs)


class SelfForbiddenMixin:
    def dispatch(self, request, *args, **kwargs):
        user = get_object_or_404(User, username=kwargs['username'])
        if request.user == user:
            messages.error(request, 'Access Denied', 'danger')
            return redirect('social_network')
        return super().dispatch(request, *args, **kwargs)


class PostOwnerRequiredMixin:
    def dispatch(self, request, *args, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])
        if request.user != post.user:
            messages.error(request, 'Access Denied', 'danger')
            return redirect(post.get_absolute_url())
        return super().dispatch(request, *args, **kwargs)
