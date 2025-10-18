from django.contrib import admin
from django.urls import path, include

# 💡 Add these lines to customize the admin panel text
admin.site.site_header = "MWASAMWADA WELL-BEING SERVICES ADMIN DASHBOARD"
admin.site.site_title = "MWASAMWADA ADMIN PORTAL"
admin.site.index_title = "Welcome to the MWASAMWADA Admin Dashboard"

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('content.urls')),
]
