from django.urls import path

from . import views


app_name = 'notifications'
urlpatterns = [
    path('', views.NotificationsView.as_view(), name='notifications'),
    path('read-all/', views.NotificationReadAllView.as_view(), name='read_all'),
    path('delete-all/', views.NotificationDeleteAllView.as_view(), name='delete_all'),
    path('<int:pk>/read/', views.NotificationReadView.as_view(), name='read'),
    path('<int:pk>/delete/', views.NotificationDeleteView.as_view(), name='delete'),
]