from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from django.forms import ValidationError

from utils.validators import (
    UsernameValidator,
    NameValidator,
    URLValidator,
)
from .models import Story, GalleryImage


User = get_user_model()


class CustomUserCreationForm(AdminUserCreationForm):
    class Meta:
        model = User
        fields = AdminUserCreationForm.Meta.fields + (
            'phone_number',
            'bio',
            'image',
            'website_url',
        )


class CustomUserChangeForm(UserChangeForm):
    class Meta:
        model = User
        fields = UserChangeForm.Meta.fields


class BaseUserForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        label='',
        validators=[UsernameValidator()],
        widget=forms.TextInput(attrs={
            'placeholder': 'Username...',
            'class': 'form-control',
        }),
    )
    email = forms.EmailField(
        label='', 
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email Address...',
            'class': 'form-control',
        }),
    )
    first_name = forms.CharField(
        max_length=15, 
        label='', 
        validators=[NameValidator('First Name')],
        widget=forms.TextInput(attrs={
            'placeholder': 'FirstName...',
            'class': 'form-control',
        }),
    )
    last_name = forms.CharField(
        max_length=15,
        label='',
        validators=[NameValidator('Last Name')],
        widget=forms.TextInput(attrs={
            'placeholder': 'LastName...',
            'class': 'form-control',
        }),
    )
    phone_number = forms.CharField(
        max_length=15,
        label='',
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone Number...',
            'class': 'form-control',
        }),
    )


class RegisterForm(BaseUserForm):
    password = forms.CharField(
        max_length=128,
        min_length=4,
        label='', 
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password...',
            'class': 'form-control',
        }),
    )
    confirm_password = forms.CharField(
        max_length=128,
        min_length=4,
        label='', 
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password...',
            'class': 'form-control',
        }),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if User.objects.filter(username=username).exists():
            raise ValidationError('This username already exists.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if User.objects.filter(email=email).exists():
            raise ValidationError('This email address already exists.')
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        if User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError('This phone number already exists.')
        return phone_number

    def clean(self):
        cd = super().clean()
        password = cd.get('password')
        confirm_password = cd.get('confirm_password')

        if password != confirm_password:
            raise ValidationError("Passwords didn't match.")


class LoginForm(forms.Form):
    username = forms.CharField(
        max_length=30, 
        label='', 
        widget=forms.TextInput(attrs={
            'placeholder': 'Username...',
            'class': 'form-control',
        }),
    )
    password = forms.CharField(
        max_length=128, 
        label='', 
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password...',
            'class': 'form-control',
        }),
    )


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        max_length=128,
        min_length=4,
        label='', 
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New Password...',
            'class': 'form-control',
        }),
    )
    confirm_password = forms.CharField(
        max_length=128,
        min_length=4,
        label='', 
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password...',
            'class': 'form-control',
        }),
    )

    def clean(self):
        cd = super().clean()
        password = cd.get('password')
        confirm_password = cd.get('confirm_password')

        if password != confirm_password:
            raise ValidationError("Passwords didn't match.")


class AccountEditForm(BaseUserForm):
    bio = forms.CharField(
        max_length=200,
        label='',
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Bio...',
            'class': 'form-control',
        }),
    )
    image = forms.ImageField(
        label='',
        required=False,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
        }),
    )
    website_url = forms.URLField(
        max_length=100,
        label='',
        required=False,
        validators=[URLValidator()],
        widget=forms.URLInput(attrs={
            'placeholder': 'Website url...',
            'class': 'form-control',
        }),
    )


class AccountDeleteForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        label='',
        validators=[UsernameValidator()],
        widget=forms.TextInput(attrs={
            'placeholder': 'Username...',
            'class': 'form-control',
        }),
    )


class StoryCreateForm(forms.ModelForm):
    class Meta:
        model = Story
        fields = ['content']
        labels = {
            'content': '',
        }
        widgets = {
            'content': forms.Textarea(attrs={
                'placeholder': 'Write your idea...',
                'class': 'form-control',
            }),
        }


class GalleryImageCreateForm(forms.ModelForm):
    class Meta:
        model = GalleryImage
        fields = ['image']
        labels = {
            'image': '',
        }
        widgets = {
            'image': forms.FileInput(attrs={
                'class': 'form-control',
            }),
        }
