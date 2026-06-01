from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.db.models import Count
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.contenttypes.models import ContentType

from notifications.models import Notification
from utils.pagination import get_pagination_context
from utils.mixins import PostOwnerRequiredMixin
from .models import Post, Like, Save
from .forms import PostCreateForm, PostUpdateForm, CommentCreateForm


User = get_user_model()


class PostListView(LoginRequiredMixin, View):
    template_name = 'posts/post_list.html'

    def get(self, request):
        post_list = Post.objects.annotate(
            likes_count=Count('likes'),
            comments_count=Count('comments'),
        ).order_by('-likes_count', '-comments_count', '-created_at')

        if request.GET.get('search'):
            search = request.GET['search']
            post_list = post_list.filter(body__icontains=search)

        return render(request, self.template_name, {
            'page_obj': get_pagination_context(request, post_list, 10),
        })


class PostCreateView(LoginRequiredMixin, View):
    template_name = 'posts/post_create.html'
    form_class = PostCreateForm

    def get(self, request):
        return render(request, self.template_name, {'form': self.form_class()})

    def post(self, request):
        form = self.form_class(request.POST, user=request.user)

        if not form.is_valid():
            return render(request, self.template_name, {'form': self.form_class()})
        
        post = form.save()
        notifications = [
            Notification(
                from_user=request.user,
                to_user=f,
                type=Notification.Type.POST,
                content_type=ContentType.objects.get_for_model(Post),
                content_id=post.id,
            )
            for f in request.user.get_follower_list()
        ]
        Notification.objects.bulk_create(notifications)

        messages.success(request, 'Post created successfully', 'success')
        return redirect(request.user.get_absolute_url())


class PostDetailView(LoginRequiredMixin, View):
    template_name = 'posts/post_detail.html'
    form_class = CommentCreateForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['pk'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, **kwargs):
        post = self.post_instance
        return render(request, self.template_name, {
            'post': post,
            'is_liked': Like.objects.filter(user=request.user, post=post).exists() or False,
            'is_saved': Save.objects.filter(user=request.user, post=post).exists() or False,
            'form': self.form_class(),
        })

    def post(self, request, **kwargs):
        post = self.post_instance
        form = self.form_class(request.POST, user=request.user, post=post)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})
        
        comment = form.save()
        
        if request.user != post.user:
            Notification.objects.create(
                from_user=request.user,
                to_user=post.user,
                type=Notification.Type.COMMENT,
                content_type=ContentType.objects.get_for_model(comment),
                object_id=comment.id,
            )

        messages.success(request, 'Comment posted successfully', 'success')
        return redirect(post.get_absolute_url())


class PostUpdateView(LoginRequiredMixin, PostOwnerRequiredMixin, View):
    template_name = 'posts/post_update.html'
    form_class = PostUpdateForm

    def setup(self, request, *args, **kwargs):
        self.post_instance = get_object_or_404(Post, pk=kwargs['pk'])
        return super().setup(request, *args, **kwargs)

    def get(self, request, **kwargs):
        return render(request, self.template_name, {
            'form': self.form_class(initial={
                'body': self.post_instance.body,
            }),
        })

    def post(self, request, **kwargs):
        form = self.form_class(request.POST, post=self.post_instance)

        if not form.is_valid():
            return render(request, self.template_name, {'form': form})
        
        form.save()
        messages.success(request, 'Post edited successfully', 'success')
        return redirect(self.post_instance.get_absolute_url())


class PostDeleteView(LoginRequiredMixin, PostOwnerRequiredMixin, View):
    def get(self, request, **kwargs):
        get_object_or_404(Post, user=request.user, pk=kwargs['pk']).delete()
        messages.success(request, 'Post deleted successfully', 'success')
        return redirect(request.user.get_post_list_url())


class PostLikeView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])

        if not Like.objects.filter(user=request.user, post=post).exists():
            like = Like.objects.create(user=request.user, post=post)

            if request.user != post.user:
                Notification.objects.create(
                    from_user=request.user,
                    to_user=post.user,
                    type=Notification.Type.LIKE,
                    content_type=ContentType.objects.get_for_model(Like),
                    object_id=like.id,
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


class PostUnsaveView(LoginRequiredMixin, View):
    def get(self, request, **kwargs):
        post = get_object_or_404(Post, pk=kwargs['pk'])
        saved = Save.objects.filter(user=request.user, post=post)

        if saved.exists():
            saved.delete()
            messages.success(request, 'Successfully unsaved post', 'success')
        return redirect(post.get_absolute_url())
