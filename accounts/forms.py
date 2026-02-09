import os

from django import forms
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.core.validators import FileExtensionValidator
from django.contrib.auth import get_user_model, authenticate
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from phonenumber_field.formfields import PhoneNumberField

from utils.validators import UsernameValidator, NameValidator, URLValidator
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


class UserBaseForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        validators=[UsernameValidator()],
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'form-control',
        }),
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={
            'placeholder': 'Email',
            'class': 'form-control',
        }),
    )
    first_name = forms.CharField(
        max_length=15, 
        validators=[NameValidator('First Name')],
        widget=forms.TextInput(attrs={
            'placeholder': 'FirstName',
            'class': 'form-control',
        }),
    )
    last_name = forms.CharField(
        max_length=15,
        validators=[NameValidator('Last Name')],
        widget=forms.TextInput(attrs={
            'placeholder': 'LastName',
            'class': 'form-control',
        }),
    )
    phone_number = PhoneNumberField(
        widget=forms.TextInput(attrs={
            'placeholder': 'Phone Number, +981234567890',
            'class': 'form-control',
        }),
    )


class UserCreateForm(UserBaseForm):
    password = forms.CharField(
        min_length=4,
        max_length=128,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control',
        }),
    )
    confirm_password = forms.CharField(
        min_length=4,
        max_length=128,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'class': 'form-control',
        }),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username and User.objects.filter(username=username).exists():
            raise ValidationError('This username already exists.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email and User.objects.filter(email=email).exists():
            raise ValidationError('This email address already exists.')
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        if phone_number and User.objects.filter(phone_number=phone_number).exists():
            raise ValidationError('This phone number already exists.')
        return phone_number

    def clean(self):
        cd = super().clean()
        password = cd.get('password')
        confirm_password = cd.get('confirm_password')

        if password and confirm_password and password != confirm_password:
            raise ValidationError("Passwords didn't match.")
        return cd
    
    def save(self):
        cd = self.cleaned_data
        cd.pop('confirm_password')
        return User.objects.create_user(**cd)


class UserLoginForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'form-control',
        }),
    )
    password = forms.CharField(
        max_length=128,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Password',
            'class': 'form-control',
        }),
    )

    def clean(self):
        cd = super().clean()
        username = cd.get('username')
        password = cd.get('password')

        if username and password:
            user = authenticate(username=username, password=password)

            if user is None:
                raise ValidationError('Wrong username or password')
            self.user = user
        return cd


class UserPasswordResetForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'form-control',
        }),
    )

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username and not User.objects.filter(username=username).exists():
            raise ValidationError('Wrong username')
        return username
    
    def save(self):
        cd = self.cleaned_data
        user = get_object_or_404(User, username=cd['username'])
        return user


class UserPasswordVerifyCodeForm(forms.Form):
    code = forms.IntegerField(
        widget=forms.NumberInput(attrs={
            'placeholder': 'Code',
            'class': 'form-control',
        }),
    )

    def __init__(self, *args, **kwargs):
        self.otp_code = kwargs.pop('otp_code', None)
        super().__init__(*args, **kwargs)

    def clean_code(self):
        code = self.cleaned_data.get('code')

        if code and code != self.otp_code:
            raise ValidationError('Wrong code')
        return code


class UserPasswordChangeForm(forms.Form):
    password = forms.CharField(
        min_length=4,
        max_length=128,
        widget=forms.PasswordInput(attrs={
            'placeholder': 'New Password',
            'class': 'form-control',
        }),
    )
    confirm_password = forms.CharField(
        min_length=4,
        max_length=128, 
        widget=forms.PasswordInput(attrs={
            'placeholder': 'Confirm Password',
            'class': 'form-control',
        }),
    )

    def __init__(self, *args, **kwargs):
        self.username = kwargs.pop('username', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cd = super().clean()
        password = cd.get('password')
        confirm_password = cd.get('confirm_password')

        if password != confirm_password:
            raise ValidationError("Passwords didn't match.")
        return cd
    
    def save(self):
        cd = self.cleaned_data
        cd.pop('confirm_password')
        
        user = get_object_or_404(User, username=self.username)
        user.set_password(cd['password'])
        user.save()
        return  user


class UserUpdateForm(UserBaseForm):
    bio = forms.CharField(
        max_length=200,
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'Bio',
            'class': 'form-control',
            'rows': 5,
        }),
    )
    image = forms.ImageField(
        required=False,
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
        }),
    )
    website_url = forms.URLField(
        max_length=100,
        required=False,
        validators=[URLValidator()],
        widget=forms.URLInput(attrs={
            'placeholder': 'Website URL',
            'class': 'form-control',
        }),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_username(self):
        username = self.cleaned_data.get('username')

        if username and User.objects.filter(username=username).exclude(pk=self.user.pk).exists():
            raise ValidationError('This username already exists.')
        return username
    
    def clean_email(self):
        email = self.cleaned_data.get('email')

        if email and User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            raise ValidationError('This email address already exists.')
        return email
    
    def clean_phone_number(self):
        phone_number = self.cleaned_data.get('phone_number')

        if phone_number and User.objects.filter(phone_number=phone_number).exclude(pk=self.user.pk).exists():
            raise ValidationError('This phone number already exists.')
        return phone_number
    
    def save(self):
        cd = self.cleaned_data

        self.user.username = cd['username']
        self.user.email = cd['email']
        self.user.first_name = cd['first_name']
        self.user.last_name = cd['last_name']
        self.user.phone_number = cd['phone_number']
        self.user.bio = cd['bio']
        self.user.website_url = cd['website_url']
        
        if not cd['image'] is None:
            if self.user.image and self.user.image.path:
                os.remove(self.user.image.path)
                self.user.image.delete()
            self.user.image = cd['image']
        
        self.user.save()
        return self.user


class UserDeleteForm(forms.Form):
    username = forms.CharField(
        max_length=30,
        validators=[UsernameValidator()],
        widget=forms.TextInput(attrs={
            'placeholder': 'Username',
            'class': 'form-control',
        }),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean(self):
        cd = super().clean()
        username = cd.get('username')

        if username and username != self.user.username:
            raise ValidationError('Wrong username')
        return cd
    
    def save(self):
        if self.user.image and self.user.image.path:
            os.remove(self.user.image.path)
            self.user.image.delete()
        self.user.delete()


class UserStoryCreateForm(forms.Form):
    content = forms.CharField(
        max_length=120,
        widget=forms.Textarea(attrs={
            'placeholder': 'Write your story...',
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

        return Story.objects.create(**cd)


class UserGalleryImageCreateForm(forms.Form):
    file = forms.FileField(
        validators=[FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'gif'])],
        widget=forms.FileInput(attrs={
            'class': 'form-control',
        }),
    )

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def save(self):
        cd = self.cleaned_data
        cd['user'] = self.user

        return GalleryImage.objects.create(**cd)
