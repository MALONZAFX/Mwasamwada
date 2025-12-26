from django.contrib import admin
from django.utils.html import format_html
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
    list_display = ['section_type_display', 'title', 'order', 'is_active', 'updated_at', 'preview_link']
    list_filter = ['section_type', 'is_active']
    list_editable = ['order', 'is_active']
    search_fields = ['title', 'content']
    readonly_fields = ['updated_at', 'preview_content']
    
    fieldsets = (
        ('Section Information', {
            'fields': ('section_type', 'title', 'content', 'order', 'is_active')
        }),
        ('Media', {
            'fields': ('image_url',),
            'classes': ('collapse',),
            'description': 'Optional: Add an image URL for this section'
        }),
        ('Preview', {
            'fields': ('preview_content',),
            'classes': ('collapse',),
            'description': 'Preview of how this section will look'
        }),
    )
    
    def section_type_display(self, obj):
        return obj.get_section_type_display()
    section_type_display.short_description = 'Section Type'
    
    def preview_link(self, obj):
        return format_html('<a href="/" target="_blank">View on Site</a>')
    preview_link.short_description = 'Preview'
    
    def preview_content(self, obj):
        """Show a preview of the content"""
        if obj.section_type == 'core_values':
            # Format core values for preview
            content = obj.content.replace('•', '<br>•')
            return format_html(f'<div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">{content}</div>')
        else:
            # Truncate for preview
            preview = obj.content[:200] + '...' if len(obj.content) > 200 else obj.content
            return format_html(f'<div style="padding: 10px; background: #f8f9fa; border-radius: 5px;">{preview}</div>')
    preview_content.short_description = 'Content Preview'
    
    # REMOVED deletion restrictions - you can now delete sections if needed
    
    # Optional: Add a warning before deleting
    def delete_view(self, request, object_id, extra_context=None):
        """Add warning before deleting guide sections"""
        extra_context = extra_context or {}
        extra_context['warning_message'] = (
            "⚠️ Warning: Deleting this guide section will remove it from the website. "
            "If this is a required section (Vision, Mission, Core Values), "
            "the website will use default content as fallback."
        )
        return super().delete_view(request, object_id, extra_context)
    
    # Optional: Add confirmation for bulk deletions
    def get_actions(self, request):
        actions = super().get_actions(request)
        # Keep all actions including delete
        return actions
    
    # Optional: Log deletions for tracking
    def save_model(self, request, obj, form, change):
        if not change:  # New object
            super().save_model(request, obj, form, change)
        else:
            # Log updates
            from django.contrib.admin.models import LogEntry, CHANGE
            from django.contrib.contenttypes.models import ContentType
            
            super().save_model(request, obj, form, change)
            
            # Log the change
            LogEntry.objects.log_action(
                user_id=request.user.pk,
                content_type_id=ContentType.objects.get_for_model(obj).pk,
                object_id=obj.pk,
                object_repr=str(obj),
                action_flag=CHANGE,
                change_message="Updated guide section"
            )