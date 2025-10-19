from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Service, ServiceBooking, ContactSubmission, NewsletterSubscriber

def index(request):
    # Get all active services with their features
    services = Service.objects.filter(is_active=True).prefetch_related('features')
    
    context = {
        'services': services,  # This matches your template
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
            booking.save()
            messages.success(request, '✅ Booking submitted successfully!')
            return redirect('/#booking')
        except Exception as e:
            print(f"Booking error: {e}")
            messages.error(request, '❌ Error submitting your booking.')
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
            messages.success(request, '✅ Message sent successfully!')
        except Exception as e:
            print(f"Contact error: {e}")
            messages.error(request, '❌ Could not send your message.')
    return redirect('/#contact')

def subscribe_newsletter(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        NewsletterSubscriber.objects.get_or_create(email=email)
        messages.success(request, '✅ Subscribed successfully!')
    return redirect('/#footer')