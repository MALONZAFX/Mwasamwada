from django.db import models
from django.core.mail import send_mail
from django.conf import settings

class Service(models.Model):
    SERVICE_CATEGORIES = [
        ('consultancy', 'Consultancy and Advisory'),
        ('counselling', 'Counselling and Psychotherapy'),
        ('training', 'Training'),
    ]

    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=SERVICE_CATEGORIES)
    description = models.TextField()
    price = models.CharField(max_length=100, default='Contact for pricing')
    icon_class = models.CharField(max_length=50, default='bi-heart-pulse')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

    def get_features_list(self):
        return [f.name for f in self.features.all()]

class Feature(models.Model):
    service = models.ForeignKey(Service, related_name='features', on_delete=models.CASCADE)
    name = models.CharField(max_length=150)

    def __str__(self):
        return f"{self.name} → {self.service.name}"

class ServiceBooking(models.Model):
    SERVICE_CHOICES = [
        ('consultancy', 'Consultancy and Advisory'),
        ('counselling', 'Counselling and Psychotherapy'),
        ('training', 'Training'),
    ]
    
    SESSION_MODE_CHOICES = [
        ('in-person', '🏢 In-Person'),
        ('online', '💻 Online'),
        ('telephone', '📞 Telephone'),
    ]

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
    session_mode = models.CharField(max_length=20, choices=SESSION_MODE_CHOICES, default='in-person')
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    description = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, default='pending', choices=[
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ])

    def __str__(self):
        return f"{self.full_name} - {self.get_service_type_display()} ({self.get_session_mode_display()})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.send_booking_email()

    def send_booking_email(self):
        try:
            admin_subject = f'🗓️ New Booking - {self.full_name}'
            admin_message = f"""
🪪 NEW BOOKING RECEIVED!

👤 CLIENT DETAILS:
• Name: {self.full_name}
• Email: {self.email}
• Phone: {self.phone}
• Service: {self.get_service_type_display()}
• Mode: {self.get_session_mode_display()}

📅 APPOINTMENT DETAILS:
• Date: {self.preferred_date}
• Time: {self.preferred_time}

📝 CLIENT'S CONCERN:
{self.description}

⏰ Submitted: {self.submitted_at}
            """

            client_subject = '🪪 Booking Confirmation - Mwasamwanda Well-being Services'
            client_message = f"""
Dear {self.full_name},

Thank you for choosing Mwasamwanda Well-being Services! Your appointment request has been received.

📋 SUMMARY:
• Service: {self.get_service_type_display()}
• Mode: {self.get_session_mode_display()}
• Date: {self.preferred_date}
• Time: {self.preferred_time}
• Phone: {self.phone}
• Email: {self.email}

We will contact you within 24 hours to confirm.

Warm regards,
Mwasambo Mwandawiro
Director
📞 +254 758 283 613
📧 mwasawellservices@gmail.com
            """

            send_mail(admin_subject, admin_message, settings.DEFAULT_FROM_EMAIL, [settings.EMAIL_HOST_USER])
            send_mail(client_subject, client_message, settings.DEFAULT_FROM_EMAIL, [self.email])
        except Exception as e:
            print(f"❌ Email error: {e}")

class ContactSubmission(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Contact from {self.name}"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.email

class Blog(models.Model):
    title = models.CharField(max_length=200)
    excerpt = models.TextField(help_text="Short description shown on blog cards")
    content = models.TextField(help_text="Full blog content shown in modal")
    image = models.ImageField(upload_to='blogs/', blank=True, null=True, help_text="Blog featured image")
    is_published = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_image_url(self):
        """Safe method to get image URL"""
        if self.image and hasattr(self.image, 'url'):
            return self.image.url
        return '/static/images/default-blog.jpg'

    class Meta:
        ordering = ['-created_at']