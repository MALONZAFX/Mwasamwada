from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.contrib import messages
import json
from django.core.mail import send_mail
from django.conf import settings
from .models import ServiceBooking, ContactSubmission, NewsletterSubscriber, Blog, Service
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

def index(request):
    services = Service.objects.filter(is_active=True)
    blogs = Blog.objects.filter(is_published=True)[:6]  # Get latest 6 blogs
    
    context = {
        'services': services,
        'blogs': blogs,
    }
    return render(request, 'index.html', context)


# ======================
# SERVICE BOOKING
# ======================
@csrf_exempt
@require_POST
def submit_booking(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        
        required_fields = ['fullName', 'email', 'phone', 'serviceType', 'sessionMode', 'preferredDate', 'preferredTime', 'description']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'success': False, 'message': f'Missing required field: {field}'}, status=400)

        # Convert date and time
        try:
            date_obj = datetime.strptime(data.get('preferredDate'), '%Y-%m-%d').date()
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid date format.'}, status=400)

        try:
            time_str = data.get('preferredTime')
            if 'AM' in time_str or 'PM' in time_str:
                time_obj = datetime.strptime(time_str, '%I:%M %p').time()
            else:
                time_obj = datetime.strptime(time_str, '%H:%M').time()
        except ValueError:
            return JsonResponse({'success': False, 'message': 'Invalid time format.'}, status=400)

        booking = ServiceBooking.objects.create(
            full_name=data.get('fullName'),
            email=data.get('email'),
            phone=data.get('phone'),
            service_type=data.get('serviceType'),
            session_mode=data.get('sessionMode'),
            preferred_date=date_obj,
            preferred_time=time_obj,
            description=data.get('description')
        )
        
        messages.success(request, "Booking submitted successfully!")
        return JsonResponse({'success': True, 'message': 'Booking submitted successfully! We will contact you soon.'})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data. Please try again.'}, status=400)
    except Exception as e:
        logger.error(f"Booking submission error: {e}")
        return JsonResponse({'success': False, 'message': 'An error occurred. Please try again.'}, status=400)


# ======================
# CONTACT FORM
# ======================
@csrf_exempt
@require_POST
def submit_contact(request):
    try:
        data = json.loads(request.body.decode('utf-8'))
        required_fields = ['name', 'email', 'subject', 'message']
        for field in required_fields:
            if not data.get(field):
                return JsonResponse({'success': False, 'message': f'Missing required field: {field}'}, status=400)
        
        ContactSubmission.objects.create(
            name=data.get('name'),
            email=data.get('email'),
            subject=data.get('subject'),
            message=data.get('message')
        )
        
        return JsonResponse({'success': True, 'message': 'Message sent successfully! We will get back to you soon.'})
    
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'message': 'Invalid JSON data. Please try again.'}, status=400)
    except Exception as e:
        logger.error(f"Contact submission error: {e}")
        return JsonResponse({'success': False, 'message': 'Error sending message. Please try again.'}, status=400)


# ======================
# FOOTER CONTACT FORM (NEW)
# ======================
@csrf_exempt
@require_POST
def footer_contact(request):
    """
    Handles quick contact form in the footer.
    """
    try:
        # decode ensures proper byte-string handling
        data = json.loads(request.body.decode('utf-8'))

        name = data.get('name', '').strip()
        email = data.get('email', '').strip()
        message = data.get('message', '').strip()

        if not name or not email or not message:
            return JsonResponse({
                'success': False,
                'message': 'Please fill in all required fields.'
            }, status=400)

        # Save message
        ContactSubmission.objects.create(
            name=name,
            email=email,
            subject="Footer Inquiry",
            message=message
        )

        # Optional: send email notification to admin
        try:
            send_mail(
                subject=f"New Footer Inquiry from {name}",
                message=f"Message:\n{message}\n\nEmail: {email}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.DEFAULT_FROM_EMAIL],
                fail_silently=True,
            )
        except Exception as e:
            logger.warning(f"Email sending failed: {e}")

        return JsonResponse({
            'success': True,
            'message': 'Thank you for reaching out! We’ll get back to you soon.'
        })

    except json.JSONDecodeError:
        return JsonResponse({
            'success': False,
            'message': 'Invalid JSON data. Please try again.'
        }, status=400)
    except Exception as e:
        logger.error(f"Footer contact error: {e}")
        return JsonResponse({
            'success': False,
            'message': 'An error occurred while submitting your message.'
        }, status=400)


# ======================
# NEWSLETTER SUBSCRIPTION
# ======================
@csrf_exempt
def subscribe_newsletter(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email', '')
            
            if not email:
                return JsonResponse({'success': False, 'message': 'Email is required.'}, status=400)
            
            # Here you can add logic to save the email to your database or send to MailChimp, etc.
            print(f"New newsletter subscription: {email}")

            return JsonResponse({'success': True, 'message': 'Thank you for subscribing!'})
        
        except json.JSONDecodeError:
            return JsonResponse({'success': False, 'message': 'Invalid JSON data.'}, status=400)
    
    return JsonResponse({'success': False, 'message': 'Only POST method is allowed.'}, status=405)