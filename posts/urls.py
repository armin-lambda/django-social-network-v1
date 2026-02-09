from django.urls import path

from . import views


app_name = 'posts'
urlpatterns = [
    path('', views.PostListView.as_view(), name='post-list'),

    path('new/', views.PostCreateView.as_view(), name='post-create'),
    
    path('edit/<int:pk>/', views.PostUpdateView.as_view(), name='post-update'),
    path('delete/<int:pk>/', views.PostDeleteView.as_view(), name='post-delete'),

    path('<int:pk>/', views.PostDetailView.as_view(), name='post-detail'),

    path('<int:pk>/like/', views.PostLikeView.as_view(), name='post-like'),
    path('<int:pk>/unlike/', views.PostUnlikeView.as_view(), name='post-unlike'),

    path('<int:pk>/save/', views.PostSaveView.as_view(), name='post-save'),
    path('<int:pk>/unsave/', views.PostUnsaveView.as_view(), name='post-unsave'),
]