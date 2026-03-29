#!/usr/bin/env python
"""
Script to add sample events to the database
Run with: python add_sample_events.py
"""

import os
import django
from datetime import datetime, timedelta

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'eventmanagement.settings')
django.setup()

from django.contrib.auth.models import User
from eventapp.models import Event

# Get or create the admin user
admin_user = User.objects.filter(username='admin').first()
if not admin_user:
    print("Admin user not found. Creating...")
    admin_user = User.objects.create_user(
        username='admin',
        email='admin@example.com',
        password='admin123',
        first_name='Admin',
        last_name='User'
    )
    admin_user.is_staff = True
    admin_user.is_superuser = True
    admin_user.save()

# Sample events data
events_data = [
    {
        'title': 'Web Development Bootcamp',
        'description': 'Intensive 8-week bootcamp covering HTML, CSS, JavaScript, React, and Node.js. Perfect for beginners looking to start a career in web development.',
        'date': datetime.now().date() + timedelta(days=7),
        'time': '09:00:00',
        'location': 'Tech Hub, San Francisco',
        'capacity': 50,
        'ticket_price': 299.99,
    },
    {
        'title': 'AI & Machine Learning Summit',
        'description': 'Join industry experts discussing the latest trends in artificial intelligence, machine learning, and deep learning. Network with professionals and learn cutting-edge techniques.',
        'date': datetime.now().date() + timedelta(days=14),
        'time': '10:00:00',
        'location': 'Convention Center, New York',
        'capacity': 200,
        'ticket_price': 149.99,
    },
    {
        'title': 'Digital Marketing Workshop',
        'description': 'Learn SEO, social media marketing, content strategy, and analytics. Hands-on workshop with real-world case studies and practical exercises.',
        'date': datetime.now().date() + timedelta(days=21),
        'time': '14:00:00',
        'location': 'Marketing Institute, Los Angeles',
        'capacity': 75,
        'ticket_price': 99.99,
    },
    {
        'title': 'Startup Pitch Competition',
        'description': 'Watch innovative startups pitch their ideas to venture capitalists and angel investors. Network with entrepreneurs and investors. Prizes up to $50,000.',
        'date': datetime.now().date() + timedelta(days=28),
        'time': '18:00:00',
        'location': 'Innovation Hub, Austin',
        'capacity': 300,
        'ticket_price': 49.99,
    },
    {
        'title': 'Cloud Computing Certification Course',
        'description': 'Comprehensive course covering AWS, Azure, and Google Cloud. Prepare for industry certifications and advance your cloud engineering career.',
        'date': datetime.now().date() + timedelta(days=35),
        'time': '09:00:00',
        'location': 'Tech Academy, Seattle',
        'capacity': 40,
        'ticket_price': 399.99,
    },
    {
        'title': 'Cybersecurity Conference 2026',
        'description': 'Leading cybersecurity experts share insights on threats, defense strategies, and best practices. Includes hands-on labs and security challenges.',
        'date': datetime.now().date() + timedelta(days=42),
        'time': '08:30:00',
        'location': 'Security Center, Boston',
        'capacity': 250,
        'ticket_price': 199.99,
    },
    {
        'title': 'Mobile App Development Hackathon',
        'description': '24-hour hackathon for iOS and Android development. Build amazing apps, win prizes, and network with fellow developers. Free food and drinks included.',
        'date': datetime.now().date() + timedelta(days=49),
        'time': '09:00:00',
        'location': 'Developer Center, Chicago',
        'capacity': 100,
        'ticket_price': 0.00,
    },
    {
        'title': 'Data Science Masterclass',
        'description': 'Advanced data science techniques including Python, R, SQL, and visualization. Learn from industry practitioners working at top tech companies.',
        'date': datetime.now().date() + timedelta(days=56),
        'time': '10:00:00',
        'location': 'Data Institute, Denver',
        'capacity': 60,
        'ticket_price': 349.99,
    },
    {
        'title': 'DevOps & Kubernetes Workshop',
        'description': 'Master containerization, orchestration, and CI/CD pipelines. Hands-on labs with Docker, Kubernetes, and Jenkins. Suitable for intermediate developers.',
        'date': datetime.now().date() + timedelta(days=63),
        'time': '13:00:00',
        'location': 'DevOps Lab, Portland',
        'capacity': 45,
        'ticket_price': 249.99,
    },
    {
        'title': 'Blockchain & Cryptocurrency Expo',
        'description': 'Explore blockchain technology, cryptocurrencies, NFTs, and DeFi. Meet blockchain developers, investors, and entrepreneurs. Live trading demonstrations.',
        'date': datetime.now().date() + timedelta(days=70),
        'time': '11:00:00',
        'location': 'Expo Center, Miami',
        'capacity': 400,
        'ticket_price': 79.99,
    },
    {
        'title': 'UX/UI Design Conference',
        'description': 'Learn modern design principles, user research, prototyping, and design systems. Keynotes from award-winning designers and interactive workshops.',
        'date': datetime.now().date() + timedelta(days=77),
        'time': '09:00:00',
        'location': 'Design Studio, San Diego',
        'capacity': 150,
        'ticket_price': 129.99,
    },
    {
        'title': 'Full Stack JavaScript Bootcamp',
        'description': 'Complete JavaScript stack including frontend (React, Vue), backend (Node.js, Express), and databases (MongoDB, PostgreSQL). 12-week intensive program.',
        'date': datetime.now().date() + timedelta(days=84),
        'time': '09:00:00',
        'location': 'Code Academy, Austin',
        'capacity': 35,
        'ticket_price': 2999.99,
    },
]

# Create events
created_count = 0
for event_data in events_data:
    # Check if event already exists
    if not Event.objects.filter(title=event_data['title']).exists():
        event = Event.objects.create(
            title=event_data['title'],
            description=event_data['description'],
            date=event_data['date'],
            time=event_data['time'],
            location=event_data['location'],
            capacity=event_data['capacity'],
            ticket_price=event_data['ticket_price'],
            created_by=admin_user,
            status=Event.STATUS_SCHEDULED,
        )
        created_count += 1
        print(f"✅ Created: {event.title}")
    else:
        print(f"⏭️  Skipped: {event_data['title']} (already exists)")

print(f"\n✨ Successfully added {created_count} new events!")
print(f"📊 Total events in database: {Event.objects.count()}")
