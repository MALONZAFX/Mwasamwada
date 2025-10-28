from django.urls import path
from . import views

urlpatterns = [
    # Homepage
    path('', views.index, name='index'),

    # API endpoints
    path('api/submit-booking/', views.submit_booking, name='submit_booking'),
    path('api/submit-contact/', views.submit_contact, name='submit_contact'),
    path('api/subscribe-newsletter/', views.subscribe_newsletter, name='subscribe_newsletter'),
    path('api/footer-contact/', views.footer_contact, name='footer_contact'),  # ✅ new route
]
