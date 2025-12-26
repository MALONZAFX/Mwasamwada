from django.contrib import admin
from .models import Service, Feature, ServiceBooking, ContactSubmission, NewsletterSubscriber, Blog, GuideSection

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
    list_display = ['full_name', 'phone', 'service_type', 'session_mode', 'preferred_date', 'preferred_time', 'status', 'submitted_at']
    list_filter = ['service_type', 'session_mode', 'status', 'submitted_at', 'preferred_date']
    search_fields = ['full_name', 'phone', 'description']
    readonly_fields = ['submitted_at']
    list_editable = ['status']
    
    fieldsets = (
        ('Client Information', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('Booking Details', {
            'fields': ('service_type', 'session_mode', 'preferred_date', 'preferred_time', 'description')
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

@admin.register(GuideSection)
class GuideSectionAdmin(admin.ModelAdmin):
    list_display = ['section_type_display', 'title', 'order', 'is_active', 'updated_at']
    list_filter = ['section_type', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'content']
    readonly_fields = ['updated_at']
    
    fieldsets = (
        ('Section Information', {
            'fields': ('section_type', 'title', 'content', 'order', 'is_active')
        }),
        ('Media', {
            'fields': ('image_url',),
            'classes': ('collapse',),
            'description': 'Optional: Add an image URL for this section'
        }),
    )
    
    def section_type_display(self, obj):
        return obj.get_section_type_display()
    section_type_display.short_description = 'Section Type'
    
    def has_delete_permission(self, request, obj=None):
        # Prevent deletion of required sections
        if obj and obj.section_type in ['vision', 'mission', 'core_values']:
            return False
        return super().has_delete_permission(request, obj)
    
    def get_actions(self, request):
        actions = super().get_actions(request)
        if 'delete_selected' in actions:
            del actions['delete_selected']
        return actions