from django.db import models
from django.core.mail import send_mail
from django.conf import settings
import logging

logger = logging.getLogger(__name__)

def safe_send_mail(subject, message, from_email, recipient_list, **kwargs):
    """Safely send email, handling configuration issues gracefully"""
    try:
        # Check if email is configured
        if not settings.EMAIL_HOST_USER or not settings.EMAIL_HOST_PASSWORD:
            logger.warning("Email not configured - skipping email send")
            return False
            
        send_mail(subject, message, from_email, recipient_list, **kwargs)
        logger.info(f"Email sent successfully to {recipient_list}")
        return True
    except Exception as e:
        logger.error(f"Email sending failed: {str(e)}")
        return False

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
    email_sent = models.BooleanField(default=False)
    email_error = models.TextField(blank=True)

    def __str__(self):
        return f"{self.full_name} - {self.get_service_type_display()} ({self.get_session_mode_display()})"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.email_sent:
            self.send_booking_email()

    def send_booking_email(self):
        try:
            # Admin notification email
            admin_subject = f'New Booking Request - {self.full_name}'
            admin_message = f"""
NEW BOOKING RECEIVED!

CLIENT DETAILS:
• Name: {self.full_name}
• Email: {self.email}
• Phone: {self.phone}
• Service: {self.get_service_type_display()}
• Mode: {self.get_session_mode_display()}

APPOINTMENT DETAILS:
• Date: {self.preferred_date}
• Time: {self.preferred_time.strftime('%I:%M %p')}

CLIENT'S CONCERN:
{self.description}

Submitted: {self.submitted_at}
            """

            # Client confirmation email
            client_subject = 'Booking Confirmation - Mwasamwanda Well-being Services'
            client_message = f"""
Dear {self.full_name},

Thank you for choosing Mwasamwanda Well-being Services! Your appointment request has been received.

BOOKING SUMMARY:
• Service: {self.get_service_type_display()}
• Mode: {self.get_session_mode_display()}
• Date: {self.preferred_date}
• Time: {self.preferred_time.strftime('%I:%M %p')}
• Phone: {self.phone}
• Email: {self.email}

We will contact you within 24 hours to confirm your appointment and provide further details.

If you have any questions, please don't hesitate to contact us.

Warm regards,
Mwasambo Mwandawiro
Director
📞 +254 758 283 613
📧 mwasawellservices@gmail.com
            """

            # Send to admin
            admin_sent = safe_send_mail(
                admin_subject, 
                admin_message.strip(),
                settings.DEFAULT_FROM_EMAIL, 
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False
            )
            
            # Send to client
            client_sent = safe_send_mail(
                client_subject, 
                client_message.strip(),
                settings.DEFAULT_FROM_EMAIL, 
                [self.email],
                fail_silently=False
            )
            
            # Mark email as sent if both were successful
            if admin_sent and client_sent:
                self.email_sent = True
                self.save(update_fields=['email_sent'])
                logger.info(f"Booking confirmation emails sent successfully for {self.full_name}")
            else:
                logger.warning(f"Some emails failed to send for booking {self.id}")
            
        except Exception as e:
            logger.error(f"Email error for booking {self.id}: {str(e)}")
            self.email_error = str(e)
            self.save(update_fields=['email_error'])

class ContactSubmission(models.Model):
    name = models.CharField(max_length=200)
    email = models.EmailField()
    subject = models.CharField(max_length=300)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    email_sent = models.BooleanField(default=False)

    def __str__(self):
        return f"Contact from {self.name}"

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.email_sent:
            self.send_contact_notification()

    def send_contact_notification(self):
        try:
            subject = f'New Contact Form Submission: {self.subject}'
            message = f"""
New contact form submission received:

Name: {self.name}
Email: {self.email}
Subject: {self.subject}

Message:
{self.message}

Submitted: {self.submitted_at}

Please respond within 24 hours.
            """

            sent = safe_send_mail(
                subject,
                message.strip(),
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False
            )
            
            if sent:
                self.email_sent = True
                self.save(update_fields=['email_sent'])
                logger.info(f"Contact notification email sent for {self.name}")
            else:
                logger.warning(f"Failed to send contact notification email for {self.name}")
            
        except Exception as e:
            logger.error(f"Failed to send contact notification email: {str(e)}")

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    welcome_email_sent = models.BooleanField(default=False)

    def __str__(self):
        return self.email

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new and not self.welcome_email_sent:
            self.send_welcome_email()

    def send_welcome_email(self):
        try:
            subject = 'Welcome to Our Newsletter!'
            message = f"""
Thank you for subscribing to our newsletter!

You'll now receive updates on our latest services, wellness tips, and special offers.

If you ever wish to unsubscribe, simply reply to this email.

Best regards,
Mwasawell Services Team
            """

            # Send welcome email to subscriber
            subscriber_sent = safe_send_mail(
                subject,
                message.strip(),
                settings.DEFAULT_FROM_EMAIL,
                [self.email],
                fail_silently=False
            )

            # Send notification to admin
            admin_subject = 'New Newsletter Subscriber'
            admin_message = f"""
New newsletter subscription:

Email: {self.email}
Subscribed: {self.subscribed_at}
            """

            admin_sent = safe_send_mail(
                admin_subject,
                admin_message.strip(),
                settings.DEFAULT_FROM_EMAIL,
                [settings.DEFAULT_FROM_EMAIL],
                fail_silently=False
            )
            
            if subscriber_sent and admin_sent:
                self.welcome_email_sent = True
                self.save(update_fields=['welcome_email_sent'])
                logger.info(f"Welcome email sent to new subscriber: {self.email}")
            else:
                logger.warning(f"Some welcome emails failed for subscriber: {self.email}")
            
        except Exception as e:
            logger.error(f"Failed to send welcome email to {self.email}: {str(e)}")

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