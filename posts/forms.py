from django import forms

from .models import Comment, Post


class PostCreateForm(forms.Form):
    body = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'placeholder': 'Write your post...',
            'class': 'form-control',
            'rows': 5,
        }),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self):
        cd = self.cleaned_data
        cd['user'] = self.user

        return Post.objects.create(**cd)


class PostUpdateForm(forms.Form):
    body = forms.CharField(
        max_length=500,
        widget=forms.Textarea(attrs={
            'placeholder': 'Write your post...',
            'class': 'form-control',
            'rows': 5,
        }),
    )

    def __init__(self, *args, **kwargs):
        self.post = kwargs.pop('post', None)
        super().__init__(*args, **kwargs)
    
    def save(self):
        cd = self.cleaned_data

        self.post.body = cd['body']
        self.post.save()
        
        return self.post


class CommentCreateForm(forms.Form):
    body = forms.CharField(
        max_length=5000,
        widget=forms.Textarea(attrs={
            'placeholder': 'Write your comment...',
            'class': 'form-control',
            'rows': 5,
        }),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        self.post = kwargs.pop('post', None)
        super().__init__(*args, **kwargs)
    
    def save(self):
        cd = self.cleaned_data
        cd['user'] = self.user
        cd['post'] = self.post

        return Comment.objects.create(**cd)

