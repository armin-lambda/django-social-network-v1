from django.urls import path

from . import views


app_name = 'accounts'
urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', views.LogoutView.as_view(), name='logout'),

    path('send-otp-code/', views.SendOTPCodeView.as_view(), name='send_otp_code'),
    path('verify-otp-code/', views.VerifyOTPCodeView.as_view(), name='verify_otp_code'),
    path('reset-password/', views.ResetPasswordView.as_view(), name='reset_password'),
    
    path('', views.PeopleView.as_view(), name='people'),

    path('edit/', views.AccountEditView.as_view(), name='edit_account'),
    path('delete-profile-image/', views.ProfileImageDeleteView.as_view(), name='delete_profile_image'),
    path('delete/', views.AccountDeleteView.as_view(), name='delete_account'),

    path('create-gallery-image/', views.GalleryImageCreateView.as_view(), name='create_gallery_image'),
    path('delete-gallery-image/<int:pk>/', views.GalleryImageDeleteView.as_view(), name='delete_gallery_image'),
    
    path('create-story/', views.StoryCreateView.as_view(), name='create_story'),
    path('delete-story/<int:pk>/', views.StoryDeleteView.as_view(), name='delete_story'),
    
    path('saved-posts/', views.SavedPostsView.as_view(), name='saved_posts'),

    path('<username>/', views.ProfileView.as_view(), name='profile'),
    
    path('<username>/follow/', views.FollowView.as_view(), name='follow'),
    path('<username>/unfollow/', views.UnfollowView.as_view(), name='unfollow'),

    path('<username>/followers/', views.FollowersView.as_view(), name='followers'),
    path('<username>/following/', views.FollowingView.as_view(), name='following'),

    path('<username>/posts/', views.PostsView.as_view(), name='posts'),
]
