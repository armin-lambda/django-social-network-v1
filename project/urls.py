from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import TemplateView


urlpatterns = [
    # Django admin panel
    path('admin/', admin.site.urls),

    # Main page
    path('', TemplateView.as_view(template_name='index.html'), name='social_network'),

    # Local apps
    path('posts/', include('posts.urls', namespace='posts')),
    path('accounts/', include('accounts.urls', namespace='accounts')),
    path('notifications/', include('notifications.urls', namespace='notifications')),
]


if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
