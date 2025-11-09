from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
import json
from django.core.mail import send_mail
from django.conf import settings
from .models import ServiceBooking, ContactSubmission, NewsletterSubscriber, Blog, Service
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)

# ======================
# PAGE VIEWS
# ======================
def index(request):
    """Home page view"""
    try:
        services = Service.objects.filter(is_active=True)
        blogs = Blog.objects.filter(is_published=True).order_by('-created_at')[:6]
        
        context = {
            'services': services,
            'blogs': blogs,
        }
        return render(request, 'index.html', context)
    except Exception as e:
        logger.error(f"Error loading index page: {str(e)}")
        return render(request, 'index.html', {'services': [], 'blogs': []})

def blog_list(request):
    """Blog listing page"""
    try:
        blogs = Blog.objects.filter(is_published=True).order_by('-created_at')
        return render(request, 'blog_list.html', {'blogs': blogs})
    except Exception as e:
        logger.error(f"Error loading blog list: {str(e)}")
        return render(request, 'blog_list.html', {'blogs': []})

def blog_detail(request, slug):
    """Blog detail page"""
    try:
        blog = get_object_or_404(Blog, slug=slug, is_published=True)
        return render(request, 'blog_detail.html', {'blog': blog})
    except Exception as e:
        logger.error(f"Error loading blog detail {slug}: {str(e)}")
        messages.error(request, "Blog post not found.")
        return render(request, 'blog_detail.html', {'blog': None})

def services_list(request):
    """Services listing page"""
    try:
        services = Service.objects.filter(is_active=True)
        return render(request, 'services_list.html', {'services': services})
    except Exception as e:
        logger.error(f"Error loading services list: {str(e)}")
        return render(request, 'services_list.html', {'services': []})

# ======================
# SERVICE BOOKING
# ======================
@csrf_exempt
@require_POST
def submit_booking(request):
    """Handle service booking form submissions"""
    try:
        # Parse JSON data
        data = json.loads(request.body.decode('utf-8'))
        logger.info(f"Booking submission received: {data.get('email', 'No email')}")
        
        # Validate required fields
        required_fields = ['fullName', 'email', 'phone', 'serviceType', 'sessionMode', 'preferredDate', 'preferredTime']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            logger.warning(f"Missing fields in booking: {missing_fields}")
            return JsonResponse({
                'success': False, 
                'message': f'Missing required fields: {", ".join(missing_fields)}'
            }, status=400)

        # Validate and convert date
        try:
            date_obj = datetime.strptime(data.get('preferredDate'), '%Y-%m-%d').date()
        except ValueError as e:
            logger.warning(f"Invalid date format in booking: {data.get('preferredDate')}")
            return JsonResponse({
                'success': False, 
                'message': 'Invalid date format. Please use YYYY-MM-DD.'
            }, status=400)

        # Validate and convert time
        try:
            time_str = data.get('preferredTime')
            if 'AM' in time_str.upper() or 'PM' in time_str.upper():
                time_obj = datetime.strptime(time_str, '%I:%M %p').time()
            else:
                time_obj = datetime.strptime(time_str, '%H:%M').time()
        except ValueError as e:
            logger.warning(f"Invalid time format in booking: {time_str}")
            return JsonResponse({
                'success': False, 
                'message': 'Invalid time format. Please use HH:MM or HH:MM AM/PM.'
            }, status=400)

        # Create booking record
        booking = ServiceBooking.objects.create(
            full_name=data.get('fullName').strip(),
            email=data.get('email').strip().lower(),
            phone=data.get('phone').strip(),
            service_type=data.get('serviceType'),
            session_mode=data.get('sessionMode'),
            preferred_date=date_obj,
            preferred_time=time_obj,
            description=data.get('description', '').strip()
        )

        logger.info(f"Booking created successfully for: {booking.email}")
        return JsonResponse({
            'success': True, 
            'message': 'Booking submitted successfully! We will contact you soon to confirm your appointment.'
        })

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in booking: {str(e)}")
        return JsonResponse({
            'success': False, 
            'message': 'Invalid form data. Please try again.'
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in booking submission: {str(e)}\n{traceback.format_exc()}")
        return JsonResponse({
            'success': False, 
            'message': 'An unexpected error occurred. Please try again or contact us directly.'
        }, status=500)

# ======================
# CONTACT FORM
# ======================
@csrf_exempt
@require_POST
def submit_contact(request):
    """Handle main contact form submissions"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        logger.info(f"Contact form submission from: {data.get('email', 'No email')}")
        
        required_fields = ['name', 'email', 'subject', 'message']
        missing_fields = [field for field in required_fields if not data.get(field)]
        
        if missing_fields:
            logger.warning(f"Missing fields in contact form: {missing_fields}")
            return JsonResponse({
                'success': False, 
                'message': f'Please fill in all required fields: {", ".join(missing_fields)}'
            }, status=400)

        # Create contact submission
        contact = ContactSubmission.objects.create(
            name=data.get('name').strip(),
            email=data.get('email').strip().lower(),
            subject=data.get('subject').strip(),
            message=data.get('message').strip()
        )

        logger.info(f"Contact form submitted successfully by: {contact.email}")
        return JsonResponse({
            'success': True, 
            'message': 'Message sent successfully! We will get back to you within 24 hours.'
        })

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in contact form: {str(e)}")
        return JsonResponse({
            'success': False, 
            'message': 'Invalid form data. Please try again.'
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in contact form: {str(e)}\n{traceback.format_exc()}")
        return JsonResponse({
            'success': False, 
            'message': 'An error occurred while sending your message. Please try again.'
        }, status=500)

# ======================
# FOOTER CONTACT FORM
# ======================
@csrf_exempt
@require_POST
def footer_contact(request):
    """Handle quick contact form in footer"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        logger.info(f"Footer contact submission from: {data.get('email', 'No email')}")

        name = data.get('name', '').strip()
        email = data.get('email', '').strip().lower()
        message = data.get('message', '').strip()

        if not name or not email or not message:
            logger.warning("Missing fields in footer contact form")
            return JsonResponse({
                'success': False,
                'message': 'Please fill in all required fields: name, email, and message.'
            }, status=400)

        # Save to database
        contact = ContactSubmission.objects.create(
            name=name,
            email=email,
            subject="Footer Quick Inquiry",
            message=message
        )

        logger.info(f"Footer contact submitted successfully by: {contact.email}")
        return JsonResponse({
            'success': True,
            'message': 'Thank you for reaching out! We\'ll get back to you within 24 hours.'
        })

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in footer contact: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Invalid form data. Please try again.'
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in footer contact: {str(e)}\n{traceback.format_exc()}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while submitting your message. Please try again.'
        }, status=500)

# ======================
# NEWSLETTER SUBSCRIPTION
# ======================
@csrf_exempt
@require_POST
def subscribe_newsletter(request):
    """Handle newsletter subscriptions"""
    try:
        data = json.loads(request.body.decode('utf-8'))
        email = data.get('email', '').strip().lower()
        
        if not email:
            return JsonResponse({
                'success': False, 
                'message': 'Please enter your email address.'
            }, status=400)

        # Validate email format
        if '@' not in email or '.' not in email:
            return JsonResponse({
                'success': False, 
                'message': 'Please enter a valid email address.'
            }, status=400)

        # Check if already subscribed
        if NewsletterSubscriber.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False, 
                'message': 'This email is already subscribed to our newsletter.'
            }, status=400)

        # Create subscription - this will automatically send welcome emails via save method
        subscriber = NewsletterSubscriber.objects.create(email=email)

        logger.info(f"New newsletter subscriber: {email}")
        return JsonResponse({
            'success': True, 
            'message': 'Thank you for subscribing! Welcome to our newsletter community.'
        })

    except json.JSONDecodeError as e:
        logger.error(f"JSON decode error in newsletter: {str(e)}")
        return JsonResponse({
            'success': False, 
            'message': 'Invalid data. Please try again.'
        }, status=400)
    except Exception as e:
        logger.error(f"Unexpected error in newsletter subscription: {str(e)}\n{traceback.format_exc()}")
        return JsonResponse({
            'success': False, 
            'message': 'An error occurred. Please try again.'
        }, status=500)

# ======================
# HEALTH CHECK & UTILITY
# ======================
@require_GET
def health_check(request):
    """Simple health check endpoint"""
    return JsonResponse({
        'status': 'healthy', 
        'service': 'Mwasawell Services API',
        'timestamp': datetime.now().isoformat()
    })

@csrf_exempt
@require_GET
def test_email(request):
    """Test email functionality (for debugging)"""
    try:
        # Test email to admin
        send_mail(
            subject='Test Email from Mwasawell Services',
            message='This is a test email to verify email configuration.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.DEFAULT_FROM_EMAIL],
            fail_silently=False,
        )
        
        # Test email to a test address (optional)
        test_email = 'test@example.com'  # Change this if you want
        send_mail(
            subject='Test Email from Mwasawell Services',
            message='This is a test email to verify client email delivery.',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[test_email],
            fail_silently=True,  # Don't fail if test email doesn't exist
        )
        
        return JsonResponse({
            'success': True, 
            'message': 'Test emails sent successfully! Check your inbox.'
        })
    except Exception as e:
        logger.error(f"Test email failed: {str(e)}")
        return JsonResponse({
            'success': False, 
            'message': f'Test email failed: {str(e)}'
        }, status=500)