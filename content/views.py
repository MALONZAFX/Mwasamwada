from django.shortcuts import render
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
import json
from .models import ServiceBooking, ContactSubmission, NewsletterSubscriber, Blog, Service

def index(request):
    services = Service.objects.filter(is_active=True)
    blogs = Blog.objects.filter(is_published=True)[:6]  # Get latest 6 blogs
    
    context = {
        'services': services,
        'blogs': blogs,
    }
    return render(request, 'index.html', context)

@csrf_exempt
@require_POST
def submit_booking(request):
    try:
        data = json.loads(request.body)
        
        # Create new booking with session mode
        booking = ServiceBooking(
            full_name=data.get('fullName'),
            email=data.get('email'),
            phone=data.get('phone'),
            service_type=data.get('serviceType'),
            session_mode=data.get('sessionMode'),
            preferred_date=data.get('preferredDate'),
            preferred_time=data.get('preferredTime'),
            description=data.get('description')
        )
        
        booking.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Booking submitted successfully! We will contact you soon.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error submitting booking. Please try again.'
        }, status=400)

@csrf_exempt
@require_POST
def submit_contact(request):
    try:
        data = json.loads(request.body)
        
        contact = ContactSubmission(
            name=data.get('name'),
            email=data.get('email'),
            subject=data.get('subject'),
            message=data.get('message')
        )
        
        contact.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Message sent successfully! We will get back to you soon.'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error sending message. Please try again.'
        }, status=400)

@csrf_exempt
@require_POST
def subscribe_newsletter(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        
        if NewsletterSubscriber.objects.filter(email=email).exists():
            return JsonResponse({
                'success': False,
                'message': 'This email is already subscribed.'
            })
        
        subscriber = NewsletterSubscriber(email=email)
        subscriber.save()
        
        return JsonResponse({
            'success': True,
            'message': 'Successfully subscribed to our newsletter!'
        })
        
    except Exception as e:
        return JsonResponse({
            'success': False,
            'message': 'Error subscribing. Please try again.'
        }, status=400)