from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

admin.site.site_header = "MWASAMWADA WELL-BEING SERVICES ADMIN DASHBOARD"
admin.site.site_title = "MWASAMWADA ADMIN PORTAL"
admin.site.index_title = "Welcome to the MWASAMWADA Admin Dashboard"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('content.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)