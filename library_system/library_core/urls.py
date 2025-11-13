from django.urls import path, include
from django.contrib import admin
from django.views.generic import RedirectView
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('core.urls')),
    path('books/', include('books.urls')),
    path('borrowings/', include('borrowings.urls')),
    path('users/', include('users.urls')),
    
    path('accounts/profile/', RedirectView.as_view(url='/', permanent=False)),
    path('accounts/login/', RedirectView.as_view(url='/users/login/', permanent=False)),
    path('accounts/logout/', RedirectView.as_view(url='/users/logout/', permanent=False)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)