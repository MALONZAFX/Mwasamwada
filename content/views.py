from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST, require_GET
from django.contrib import messages
import json
from django.core.mail import send_mail
from django.conf import settings
from .models import ServiceBooking, ContactSubmission, NewsletterSubscriber, Blog, Service, GuideSection
from datetime import datetime
import logging
import traceback

logger = logging.getLogger(__name__)

# ======================
# HELPER FUNCTIONS
# ======================
def get_guide_sections():
    """Get guide sections from database with fallback to defaults"""
    try:
        sections = GuideSection.objects.filter(is_active=True).order_by('order')
        
        # If no sections exist, create default ones
        if not sections.exists():
            sections = create_default_guide_sections()
        
        # Ensure we have all three required sections
        required_sections = ['vision', 'mission', 'core_values']
        existing_types = [section.section_type for section in sections]
        
        for section_type in required_sections:
            if section_type not in existing_types:
                create_default_section(section_type)
                # Re-fetch sections
                sections = GuideSection.objects.filter(is_active=True).order_by('order')
        
        return sections
        
    except Exception as e:
        logger.error(f"Error getting guide sections: {str(e)}")
        return get_default_guide_sections_fallback()

def create_default_guide_sections():
    """Create default guide sections in database"""
    default_sections = [
        {
            'section_type': 'vision',
            'title': 'Our Vision',
            'content': 'Being a strategic global leader in enhancing normative development and mental health through effective professional, evidence-based and innovative psychological interventions.',
            'image_url': 'https://thumbs.dreamstime.com/b/our-vision-drawn-white-brick-wall-d-inscription-modern-illustation-blue-arrow-hand-icons-around-brickwall-89018617.jpg',
            'order': 1,
            'is_active': True
        },
        {
            'section_type': 'mission',
            'title': 'Our Mission',
            'content': 'Developing and using effective professional, evidence-based and innovative psychological interventions through consultancy and advisory, counselling/psychotherapy and training to enhance normative development and mental health at individual and group levels across the lifespan.',
            'image_url': 'https://www.energyquestmagazine.com/wp-content/uploads/2017/02/mission.jpg',
            'order': 2,
            'is_active': True
        },
        {
            'section_type': 'core_values',
            'title': 'Our Core Values',
            'content': """• Empowerment – Enabling people to exploit their potential as expected.
• Professionalism – Upholding competence, responsibility and accountability in service delivery.
• Innovation – Embracing creativity in service delivery.
• Client-centred – Doing all for the best for the clients' interests.""",
            'image_url': 'https://www.v3co.com/wp-content/uploads/2023/10/Our-Core-Values-blog-header.png',
            'order': 3,
            'is_active': True
        }
    ]
    
    created_sections = []
    for section_data in default_sections:
        section, created = GuideSection.objects.get_or_create(
            section_type=section_data['section_type'],
            defaults=section_data
        )
        created_sections.append(section)
    
    return GuideSection.objects.filter(is_active=True).order_by('order')

def create_default_section(section_type):
    """Create a single default section"""
    section_data = {
        'vision': {
            'title': 'Our Vision',
            'content': 'Being a strategic global leader in enhancing normative development and mental health through effective professional, evidence-based and innovative psychological interventions.',
            'image_url': 'https://thumbs.dreamstime.com/b/our-vision-drawn-white-brick-wall-d-inscription-modern-illustation-blue-arrow-hand-icons-around-brickwall-89018617.jpg',
            'order': 1,
            'is_active': True
        },
        'mission': {
            'title': 'Our Mission',
            'content': 'Developing and using effective professional, evidence-based and innovative psychological interventions through consultancy and advisory, counselling/psychotherapy and training to enhance normative development and mental health at individual and group levels across the lifespan.',
            'image_url': 'https://www.energyquestmagazine.com/wp-content/uploads/2017/02/mission.jpg',
            'order': 2,
            'is_active': True
        },
        'core_values': {
            'title': 'Our Core Values',
            'content': """• Empowerment – Enabling people to exploit their potential as expected.
• Professionalism – Upholding competence, responsibility and accountability in service delivery.
• Innovation – Embracing creativity in service delivery.
• Client-centred – Doing all for the best for the clients' interests.""",
            'image_url': 'https://www.v3co.com/wp-content/uploads/2023/10/Our-Core-Values-blog-header.png',
            'order': 3,
            'is_active': True
        }
    }
    
    if section_type in section_data:
        GuideSection.objects.get_or_create(
            section_type=section_type,
            defaults=section_data[section_type]
        )

def get_default_guide_sections_fallback():
    """Return default guide sections as dicts for template fallback"""
    return [
        {
            'section_type': 'vision',
            'title': 'Our Vision',
            'content': 'Being a strategic global leader in enhancing normative development and mental health through effective professional, evidence-based and innovative psychological interventions.',
            'image_url': 'https://thumbs.dreamstime.com/b/our-vision-drawn-white-brick-wall-d-inscription-modern-illustation-blue-arrow-hand-icons-around-brickwall-89018617.jpg',
            'order': 1
        },
        {
            'section_type': 'mission',
            'title': 'Our Mission',
            'content': 'Developing and using effective professional, evidence-based and innovative psychological interventions through consultancy and advisory, counselling/psychotherapy and training to enhance normative development and mental health at individual and group levels across the lifespan.',
            'image_url': 'https://www.energyquestmagazine.com/wp-content/uploads/2017/02/mission.jpg',
            'order': 2
        },
        {
            'section_type': 'core_values',
            'title': 'Our Core Values',
            'content': """• Empowerment – Enabling people to exploit their potential as expected.
• Professionalism – Upholding competence, responsibility and accountability in service delivery.
• Innovation – Embracing creativity in service delivery.
• Client-centred – Doing all for the best for the clients' interests.""",
            'image_url': 'https://www.v3co.com/wp-content/uploads/2023/10/Our-Core-Values-blog-header.png',
            'order': 3
        }
    ]

# ======================
# PAGE VIEWS
# ======================
def index(request):
    """Home page view"""
    try:
        # Get all required data
        services = Service.objects.filter(is_active=True)
        blogs = Blog.objects.filter(is_published=True).order_by('-created_at')[:6]
        guide_sections = get_guide_sections()
        
        context = {
            'services': services,
            'blogs': blogs,
            'guide_sections': guide_sections,
        }
        return render(request, 'index.html', context)
        
    except Exception as e:
        logger.error(f"Error loading index page: {str(e)}\n{traceback.format_exc()}")
        
        # Fallback context in case of error
        context = {
            'services': Service.objects.filter(is_active=True) if Service.objects.exists() else [],
            'blogs': Blog.objects.filter(is_published=True).order_by('-created_at')[:6] if Blog.objects.exists() else [],
            'guide_sections': get_default_guide_sections_fallback(),
        }
        return render(request, 'index.html', context)

def blog_list(request):
    """Blog listing page"""
    try:
        blogs = Blog.objects.filter(is_published=True).order_by('-created_at')
        context = {
            'blogs': blogs,
        }
        return render(request, 'blog_list.html', context)
        
    except Exception as e:
        logger.error(f"Error loading blog list: {str(e)}")
        return render(request, 'blog_list.html', {'blogs': []})

def blog_detail(request, slug):
    """Blog detail page"""
    try:
        blog = get_object_or_404(Blog, slug=slug, is_published=True)
        context = {
            'blog': blog,
        }
        return render(request, 'blog_detail.html', context)
        
    except Exception as e:
        logger.error(f"Error loading blog detail {slug}: {str(e)}")
        messages.error(request, "Blog post not found.")
        return render(request, 'blog_detail.html', {'blog': None})

def services_list(request):
    """Services listing page"""
    try:
        services = Service.objects.filter(is_active=True)
        context = {
            'services': services,
        }
        return render(request, 'services_list.html', context)
        
    except Exception as e:
        logger.error(f"Error loading services list: {str(e)}")
        return render(request, 'services_list.html', {'services': []})

def guide_sections_api(request):
    """API endpoint to get guide sections (for AJAX if needed)"""
    try:
        sections = get_guide_sections()
        data = []
        
        for section in sections:
            data.append({
                'section_type': section.section_type,
                'title': section.title,
                'content': section.content,
                'image_url': section.image_url,
                'order': section.order,
            })
        
        return JsonResponse({
            'success': True,
            'sections': data,
            'count': len(data)
        })
        
    except Exception as e:
        logger.error(f"Error in guide sections API: {str(e)}")
        return JsonResponse({
            'success': False,
            'message': 'Failed to load guide sections',
            'sections': get_default_guide_sections_fallback()
        })

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
    try:
        # Check if database has guide sections
        guide_sections_count = GuideSection.objects.count()
        services_count = Service.objects.count()
        blogs_count = Blog.objects.count()
        
        return JsonResponse({
            'status': 'healthy', 
            'service': 'Mwasawell Services API',
            'database': {
                'guide_sections': guide_sections_count,
                'services': services_count,
                'blogs': blogs_count
            },
            'timestamp': datetime.now().isoformat()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'degraded',
            'error': str(e),
            'timestamp': datetime.now().isoformat()
        }, status=500)

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

# ======================
# GUIDE SECTION MANAGEMENT VIEWS (Optional for admin interface)
# ======================
def manage_guide_sections(request):
    """Admin view to manage guide sections (requires admin permissions)"""
    if not request.user.is_staff:
        return render(request, '403.html', status=403)
    
    try:
        sections = GuideSection.objects.all().order_by('order')
        context = {
            'sections': sections,
        }
        return render(request, 'admin/guide_sections.html', context)
    except Exception as e:
        logger.error(f"Error in manage_guide_sections: {str(e)}")
        return render(request, 'admin/guide_sections.html', {'sections': []})