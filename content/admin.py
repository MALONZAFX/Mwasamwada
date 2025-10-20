from django.contrib import admin
from .models import Service, Feature, ServiceBooking, ContactSubmission, NewsletterSubscriber, Blog

class FeatureInline(admin.TabularInline):
    model = Feature
    extra = 1

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'price', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['name', 'description']
    list_editable = ['is_active', 'price']
    inlines = [FeatureInline]
    
    fieldsets = (
        ('Service Information', {
            'fields': ('name', 'category', 'description', 'price')
        }),
        ('Display Settings', {
            'fields': ('icon_class', 'is_active'),
            'description': 'Icon class examples: bi-heart-pulse, bi-person, bi-chat-dots, bi-mortarboard'
        }),
    )

@admin.register(Feature)
class FeatureAdmin(admin.ModelAdmin):
    list_display = ['name', 'service']
    list_filter = ['service']
    search_fields = ['name', 'service__name']

@admin.register(ServiceBooking)
class ServiceBookingAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'phone', 'service_type', 'session_mode', 'preferred_date', 'preferred_time', 'status', 'submitted_at']  # ADDED session_mode
    list_filter = ['service_type', 'session_mode', 'status', 'submitted_at', 'preferred_date']  # ADDED session_mode
    search_fields = ['full_name', 'phone', 'description']
    readonly_fields = ['submitted_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Client Information', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Booking Details', {
            'fields': ('service_type', 'session_mode', 'preferred_date', 'preferred_time', 'description')  # ADDED session_mode
        }),
        ('Status', {
            'fields': ('status', 'submitted_at')
        }),
    )

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

@admin.register(Blog)
class BlogAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_published', 'created_at', 'updated_at']
    list_filter = ['is_published', 'created_at']
    search_fields = ['title', 'excerpt', 'content']
    list_editable = ['is_published']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Blog Content', {
            'fields': ('title', 'excerpt', 'content', 'image')
        }),
        ('Publication Settings', {
            'fields': ('is_published', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )