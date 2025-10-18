import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mwasa.settings')
django.setup()

from content.models import WebsiteContent

def create_initial_content():
    # Hero Section Content
    hero_content = [
        ('site_name', 'Mwasamwanda', 'hero', 'Main website name in header'),
        ('site_title', 'Mwasamwanda', 'hero', 'Browser tab title'),
        ('hero_tagline', 'Empowerment, Enhanced Productivity, Happy Life', 'hero', 'Hero section tagline'),
        ('hero_title', 'Enhancing Normative Development and Mental Health Across the Lifespan', 'hero', 'Main hero title'),
        ('hero_description', 'Mwasamwanda Well-being Services facilitates normative development and mental health through professional, evidence-based psychological interventions for individuals and groups.', 'hero', 'Hero description text'),
        ('stat1_title', 'Professional Psychologists', 'hero', 'First statistic title'),
        ('stat1_description', 'Competent and experienced team', 'hero', 'First statistic description'),
        ('stat2_title', 'Evidence-Based Methods', 'hero', 'Second statistic title'),
        ('stat2_description', 'Using proven psychological interventions', 'hero', 'Second statistic description'),
        ('stat3_title', 'Global Standards', 'hero', 'Third statistic title'),
        ('stat3_description', 'Following current professional trends', 'hero', 'Third statistic description'),
        ('stat4_title', 'Across Lifespan', 'hero', 'Fourth statistic title'),
        ('stat4_description', 'Services for all age groups', 'hero', 'Fourth statistic description'),
    ]

    # Services Content
    services_content = [
        ('services_title', 'Professional Psychological Services', 'service', 'Services section main title'),
        ('services_subtitle', 'Evidence-based interventions designed to enhance normative development and mental health across the lifespan', 'service', 'Services section subtitle'),
        
        ('service1_title', 'Consultancy & Advisory', 'service', 'First service title'),
        ('service1_price', 'KSh 5,000', 'service', 'First service price'),
        ('service1_description', 'Professional psychological consultancy including policy formulation, program planning, research design, and psychological assessment.', 'service', 'First service description'),
        
        ('service2_title', 'Counselling & Psychotherapy', 'service', 'Second service title'),
        ('service2_price', 'KSh 3,500/session', 'service', 'Second service price'),
        ('service2_description', 'Professional therapy services across the lifespan to help individuals deal with issues limiting normative development and mental health.', 'service', 'Second service description'),
        
        ('service3_title', 'Training Programs', 'service', 'Third service title'),
        ('service3_price', 'KSh 8,000 - 15,000', 'service', 'Third service price'),
        ('service3_description', 'Comprehensive training programs to build capacity in organizations, institutions, and communities on normative development and mental health.', 'service', 'Third service description'),
        
        ('service4_title', 'Mind Transformation Coaching', 'service', 'Fourth service title'),
        ('service4_price', 'KSh 6,000/session', 'service', 'Fourth service price'),
        ('service4_description', 'Specialized coaching services focusing on personal development, mindset transformation, and enhanced productivity.', 'service', 'Fourth service description'),
    ]

    # Contact Content
    contact_content = [
        ('contact_title', 'Contact Mwasamwanda Well-being Services', 'contact', 'Contact section title'),
        ('contact_subtitle', 'Get in touch with us to discuss your mental health needs or schedule a consultation.', 'contact', 'Contact section subtitle'),
        ('phone_number', '0758283613', 'contact', 'Primary phone number'),
        ('email_address', 'mwasawellservices@gmail.com', 'contact', 'Primary email address'),
        ('address_line1', 'Southern House, Murang\'a Road', 'contact', 'Address line 1'),
        ('address_line2', 'Off Mot Avenue, Fourth Floor', 'contact', 'Address line 2'),
        ('address_line3', 'Nairobi, KENYA', 'contact', 'Address line 3'),
        ('hours_weekdays', 'Mon-Fri: 8:00 AM - 6:00 PM', 'contact', 'Weekday business hours'),
        ('hours_weekend', 'Sat: 9:00 AM - 2:00 PM', 'contact', 'Weekend business hours'),
    ]

    # Combine all content
    all_content = hero_content + services_content + contact_content

    created_count = 0
    updated_count = 0

    for key, value, content_type, description in all_content:
        obj, created = WebsiteContent.objects.get_or_create(
            key=key,
            defaults={
                'value': value,
                'content_type': content_type,
                'description': description
            }
        )
        
        if created:
            created_count += 1
        else:
            # Update existing content
            obj.value = value
            obj.content_type = content_type
            obj.description = description
            obj.save()
            updated_count += 1

    print(f"Content creation completed!")
    print(f"Created: {created_count} new items")
    print(f"Updated: {updated_count} existing items")

if __name__ == '__main__':
    create_initial_content()