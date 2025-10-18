from django.contrib import admin
from .models import Service, ServiceBooking, ContactSubmission, NewsletterSubscriber

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'icon_class', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description', 'features']
    list_editable = ['is_active', 'icon_class']
    
    fieldsets = (
        ('Service Information', {
            'fields': ('name', 'category', 'description')
        }),
        ('Features & Display', {
            'fields': ('features', 'icon_class', 'is_active'),
            'description': 'Enter features separated by commas. Icon class should be like "bi-heart-pulse"'
        }),
    )

@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'service_type', 'preferred_date', 'preferred_time', 'status', 'submitted_at']
    list_filter = ['service_type', 'status', 'submitted_at', 'preferred_date']
    search_fields = ['full_name', 'phone', 'description']
    readonly_fields = ['submitted_at']
    list_editable = ['status']


@admin.register(ContactSubmission)
class ContactSubmissionAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'submitted_at', 'is_read']
    list_filter = ['is_read', 'submitted_at']
    search_fields = ['name', 'email', 'subject']
    readonly_fields = ['submitted_at']
    list_editable = ['is_read']

@admin.register(NewsletterSubscriber)
class NewsletterSubscriberAdmin(admin.ModelAdmin):
    list_display = ['email', 'subscribed_at', 'is_active']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email']
    list_editable = ['is_active']