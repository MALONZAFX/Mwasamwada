from django.db import models
from django.core.mail import send_mail
from django.conf import settings

class Service(models.Model):
    SERVICE_CATEGORIES = [
        ('consultancy', 'Consultancy & Advisory Services'),
        ('counselling', 'Counselling & Psychotherapy Services'),
        ('training', 'Training & Capacity Building Services'),

    ]
    
    name = models.CharField(max_length=200)
    category = models.CharField(max_length=20, choices=SERVICE_CATEGORIES)
    description = models.TextField()
    price = models.CharField(max_length=100, default='Contact for pricing')
    features = models.TextField(help_text="Enter features separated by commas")
    icon_class = models.CharField(max_length=50, default='bi-heart-pulse')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.name
    
    def get_features_list(self):
        return [feature.strip() for feature in self.features.split(',')]

class ServiceBooking(models.Model):
    SERVICE_CHOICES = [
        ('individual', 'Individual & Family Services'),
        ('organizational', 'Organizational & Training Services'),
    ]
    
    full_name = models.CharField(max_length=200)
    email = models.EmailField()  # ADDED EMAIL FIELD
    phone = models.CharField(max_length=20)
    service_type = models.CharField(max_length=20, choices=SERVICE_CHOICES)
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
        return f"{self.full_name} - {self.get_service_type_display()}"
    
    def save(self, *args, **kwargs):
        is_new = self.pk is None  # Check if this is a new booking
        super().save(*args, **kwargs)
        
        # Send email only for new bookings
        if is_new:
            self.send_booking_email()
    
    def send_booking_email(self):
        """Send email to admin AND confirmation email to client"""
        try:
            from django.core.mail import send_mail
            from django.conf import settings
            
            # EMAIL 1: TO ADMIN (Notification)
            admin_subject = f'🗓️ New Booking - {self.full_name}'
            admin_message = f"""
🪪 NEW BOOKING RECEIVED! 

👤 CLIENT DETAILS:
• Name: {self.full_name}
• Email: {self.email}
• Phone: {self.phone}
• Service: {self.get_service_type_display()}

📅 APPOINTMENT DETAILS:
• Date: {self.preferred_date}
• Time: {self.preferred_time}

📝 CLIENT'S CONCERN:
{self.description}

⏰ Submitted: {self.submitted_at}

💼 Please check the admin panel and contact the client to confirm.

Best regards,
Mwasamwanda Well-being Services Booking System
            """

            # EMAIL 2: TO CLIENT (Confirmation)
            client_subject = '🪪 Booking Confirmation From Your Website - Mwasamwanda Well-being Services'
            client_message = f"""
Dear {self.full_name},

Thank you for choosing Mwasamwanda Well-being Services! We have successfully received your appointment request.

📋 YOUR BOOKING SUMMARY:
• Service: {self.get_service_type_display()}
• Preferred Date: {self.preferred_date}
• Preferred Time: {self.preferred_time}
• Contact Phone: {self.phone}
• Contact Email: {self.email}

🔔 WHAT HAPPENS NEXT:
1. We will contact you within 24 hours at your provided phone number
2. We'll confirm your appointment time and date
3. We'll discuss any preliminary details

If you have any urgent questions, please don't hesitate to call us directly at +254 758 283 613.

We're honored to be part of your mental wellness journey and look forward to supporting you!

Warm regards,
Mwasambo Mwandawiro
Director
Mwasamwanda Well-being Services

📍 Contact Information:
📞 +254 758 283 613
📧 mwasawellservices@gmail.com
🌐 Your mental wellness is our priority
            """

            # Send to ADMIN
            send_mail(
                admin_subject,
                admin_message.strip(),
                settings.DEFAULT_FROM_EMAIL,
                [settings.EMAIL_HOST_USER],  # To admin
                fail_silently=False,
            )
            print("✅ Admin notification email sent successfully!")

            # Send to CLIENT
            send_mail(
                client_subject,
                client_message.strip(),
                settings.DEFAULT_FROM_EMAIL,
                [self.email],  # To client
                fail_silently=False,
            )
            print("✅ Client confirmation email sent successfully!")
            
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