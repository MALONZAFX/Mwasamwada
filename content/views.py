from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Service, ServiceBooking, ContactSubmission, NewsletterSubscriber

def index(request):
    services = Service.objects.filter(is_active=True)
    
    # Group services by category
    individual_services = services.filter(category='individual')
    organizational_services = services.filter(category='organizational')
    
    context = {
        'individual_services': individual_services,
        'organizational_services': organizational_services,
    }
    return render(request, 'index.html', context)

def submit_booking(request):
    if request.method == 'POST':
        try:
            booking = ServiceBooking(
                full_name=request.POST.get('fullName'),
                email=request.POST.get('email'),
                phone=request.POST.get('phone'),
                service_type=request.POST.get('serviceType'),
                preferred_date=request.POST.get('preferredDate'),
                preferred_time=request.POST.get('preferredTime'),
                description=request.POST.get('description')
            )
            booking.save()  # This will trigger the email
            
            messages.success(request, '✅ Booking submitted successfully! We will contact you within 24 hours to confirm.')
            return redirect('/#booking')
            
        except Exception as e:
            print(f"Booking error: {e}")  # Debug
            messages.error(request, '❌ There was an error submitting your booking. Please try again or call us directly.')
            return redirect('/#booking')
    
    return redirect('/')

def submit_contact(request):
    if request.method == 'POST':
        try:
            ContactSubmission.objects.create(
                name=request.POST.get('name'),
                email=request.POST.get('email'),
                subject=request.POST.get('subject'),
                message=request.POST.get('message')
            )
            messages.success(request, '✅ Thank you for your message! We will get back to you soon.')
            return redirect('/#contact')
        except:
            messages.error(request, '❌ There was an error sending your message. Please try again.')
            return redirect('/#contact')
    return redirect('/')

def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        try:
            NewsletterSubscriber.objects.get_or_create(email=email)
            messages.success(request, '✅ Thank you for subscribing to our newsletter!')
            return redirect('/#footer')
        except:
            messages.error(request, '❌ There was an error with your subscription. Please try again.')
            return redirect('/#footer')
    return redirect('/')