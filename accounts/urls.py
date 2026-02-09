from django.urls import path

from . import views


app_name = 'accounts'
urlpatterns = [
    path('register/', views.UserCreateView.as_view(), name='user-create'),
    path('login/', views.UserLoginView.as_view(), name='user-login'),
    path('logout/', views.UserLogoutView.as_view(), name='user-logout'),

    path('reset-password/', views.UserPasswordResetView.as_view(), name='user-password-reset'),
    path('verify-code/', views.UserPasswordVerifyCodeView.as_view(), name='user-password-verify-code'),
    path('change-password/', views.UserPasswordChangeView.as_view(), name='user-password-change'),
    
    path('', views.UserListView.as_view(), name='user-list'),

    path('edit-profile/', views.UserUpdateView.as_view(), name='user-update'),
    path('delete-profile-image/', views.UserProfileImageDeleteView.as_view(), name='user-profile-image-delete'),
    path('delete/', views.UserDeleteView.as_view(), name='user-delete'),

    path('create-gallery-image/', views.UserGalleryImageCreateView.as_view(), name='user-gallery-image-create'),
    path('delete-gallery-image/<int:pk>/', views.UserGalleryImageDeleteView.as_view(), name='user-gallery-image-delete'),
    
    path('create-story/', views.UserStoryCreateView.as_view(), name='user-story-create'),
    path('delete-story/<int:pk>/', views.UserStoryDeleteView.as_view(), name='user-story-delete'),
    
    path('saved-posts/', views.UserSavedPostListView.as_view(), name='user-saved-post-list'),

    path('<username>/', views.UserDetailView.as_view(), name='user-detail'),
    
    path('<username>/follow/', views.UserFollowView.as_view(), name='user-follow'),
    path('<username>/unfollow/', views.UserUnfollowView.as_view(), name='user-unfollow'),

    path('<username>/followers/', views.UserFollowerListView.as_view(), name='user-follower-list'),
    path('<username>/following/', views.UserFollowingListView.as_view(), name='user-following-list'),

    path('<username>/posts/', views.UserPostListView.as_view(), name='user-post-list'),
]
