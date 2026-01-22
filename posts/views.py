from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Count

from notifications.models import Notification
from utils.pagination import get_pagination_context
from utils.mixins import PostOwnerRequiredMixin
from .models import Post, Like, Save
from .forms import CommentForm, PostCreateEditForm


User = get_user_model()


class PostsView(LoginRequiredMixin, View):
    template_name = 'posts/posts.html'

    def get(self, request):
        # posts = Post.objects.all()
        posts = Post.objects.annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments'),
        ).order_by('-likes_count', '-comments_count', '-created_at')

        if request.GET.get('search'):
            search = request.GET['search']
            posts = posts.filter(body__icontains=search)

        return render(request, self.template_name, {
            'page_obj': get_pagination_context(request, posts, 10),
        })


class PostCreateView(LoginRequiredMixin, View):
    template_name = 'posts/post_create.html'
    form_class = PostCreateEditForm

    def get(self, request):
        return render(request, self.template_name, {
            'form': self.form_class(),
        })

    def post(self, request):
        form = self.form_class(request.POST)

        if form.is_valid():
            user = request.user
            post = form.save(commit=False)
            post.user = user
            post.save()

            followers = user.get_followers()
            notifications = [
                Notification(
                    from_user=post.user,
                    to_user=f,
                    notification_type='post',
                    post=post,
                )
                for f in followers
            ]

            Notification.objects.bulk_create(notifications)
            messages.success(request, 'Successfully created post.', 'success')
            return redirect(user.get_profile_url())
        return render(request, self.template_name, {
            'form': form,
        })


class PostDetailView(LoginRequiredMixin, View):
    template_name = 'posts/post_detail.html'
    form_class = CommentForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['pk'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, **kwargs):
        post = self.post_instance
        comments = post.comments.all()
        return render(request, self.template_name, {
            'post': post,
            'is_liked': Like.objects.filter(user=request.user, post=post).exists() or False,
            'is_saved': Save.objects.filter(user=request.user, post=post).exists() or False,
            'comments': comments,
            'form': self.form_class(),
        })

    def post(self, request, **kwargs):
        post = self.post_instance
        comments = post.comments.all()
        form = self.form_class(request.POST)

        if form.is_valid():
            comment = form.save(commit=False)
            comment.user = request.user
            comment.post = post
            comment.save()
            
            if not request.user == post.user:
                Notification.objects.create(
                    from_user=request.user,
                    to_user=post.user,
                    notification_type='comment',
                    comment=comment,
                )
            messages.success(request, 'Successfully sent comment.', 'success')
            return redirect(post.get_absolute_url())
        return render(request, self.template_name, {
            'post': post,
            'comments': comments,
            'form': form,
        })


class PostEditView(LoginRequiredMixin, PostOwnerRequiredMixin, View):
    template_name = 'posts/post_edit.html'
    form_class = PostCreateEditForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['pk'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, **kwargs):
        post = self.post_instance
        return render(request, self.template_name, {
            'form': self.form_class(instance=post),
        })

    def post(self, request, **kwargs):
        post = self.post_instance
        form = self.form_class(request.POST, instance=post)

        if form.is_valid():
            post = form.save()
            post.user = request.user
            post.save()
            messages.success(request, 'Successfully edited post', 'success')
            return redirect(post.get_absolute_url())
        return render(request, self.template_name, {
            'form': form,
        })


class PostDeleteView(LoginRequiredMixin, PostOwnerRequiredMixin, View):
    def get(self, request, **kwargs):
        get_object_or_404(Post, user=request.user, pk=kwargs['pk']).delete()
        messages.success(request, 'Successfully deleted post', 'success')
        return redirect(request.user.get_posts_url())


class PostLikeView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])

        if not Like.objects.filter(user=request.user, post=post).exists():
            like = Like.objects.create(user=request.user, post=post)

            if request.user != post.user:
                Notification.objects.create(
                    from_user=request.user,
                    to_user=post.user,
                    notification_type='like',
                    like=like
                )
        
            messages.success(request, 'Successfully liked post', 'success')
        return redirect(post.get_absolute_url())


class PostUnlikeView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])
        like = Like.objects.filter(user=request.user, post=post)

        if like.exists():
            like.delete()
            messages.success(request, 'Successfully unliked post', 'success')
        return redirect(post.get_absolute_url())


class PostSaveView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])

        if not Save.objects.filter(user=request.user, post=post).exists():
            Save.objects.create(user=request.user, post=post)
            messages.success(request, 'Successfully saved post', 'success')
        return redirect(post.get_absolute_url())


class PostUnSaveView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])
        saved = Save.objects.filter(user=request.user, post=post)

        if saved.exists():
            saved.delete()
            messages.success(request, 'Successfully unsaved post', 'success')
        return redirect(post.get_absolute_url())