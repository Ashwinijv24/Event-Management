from django.core.mail import send_mail
from django.conf import settings
from django.db.models import Sum, Count, Q
from django.utils import timezone
from .models import Event, Registration, Payment
import io
from datetime import datetime, timedelta

def send_confirmation_email(registration):
    """Send confirmation email to attendee"""
    subject = f'Registration Confirmed - {registration.event.title}'
    message = f"""
    Dear {registration.attendee.get_full_name() or registration.attendee.username},
    
    Your registration for {registration.event.title} has been confirmed!
    
    Event Details:
    - Date: {registration.event.date}
    - Time: {registration.event.time or 'TBA'}
    - Location: {registration.event.location}
    - Ticket Number: {registration.ticket_number}
    
    Amount Paid: ${registration.amount_paid}
    
    Please keep this ticket number for entry.
    
    Thank you!
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [registration.attendee.email],
        fail_silently=True,
    )
    registration.confirmation_sent = True
    registration.save()

def send_event_reminder(registration):
    """Send event reminder to attendee"""
    subject = f'Reminder - {registration.event.title} Tomorrow'
    message = f"""
    Dear {registration.attendee.get_full_name() or registration.attendee.username},
    
    This is a reminder that {registration.event.title} is tomorrow!
    
    Event Details:
    - Date: {registration.event.date}
    - Time: {registration.event.time or 'TBA'}
    - Location: {registration.event.location}
    - Ticket Number: {registration.ticket_number}
    
    We look forward to seeing you there!
    """
    
    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [registration.attendee.email],
        fail_silently=True,
    )
    registration.reminder_sent = True
    registration.save()

def generate_registration_report(event=None, start_date=None, end_date=None):
    """Generate registration report"""
    registrations = Registration.objects.select_related('event', 'attendee')
    
    if event:
        registrations = registrations.filter(event=event)
    if start_date:
        registrations = registrations.filter(registered_at__gte=start_date)
    if end_date:
        registrations = registrations.filter(registered_at__lte=end_date)
    
    report = {
        'total_registrations': registrations.count(),
        'completed_payments': registrations.filter(payment_status=Registration.PAYMENT_COMPLETED).count(),
        'pending_payments': registrations.filter(payment_status=Registration.PAYMENT_PENDING).count(),
        'failed_payments': registrations.filter(payment_status=Registration.PAYMENT_FAILED).count(),
        'registrations': registrations.order_by('-registered_at')
    }
    
    return report

def generate_revenue_report(event=None, start_date=None, end_date=None):
    """Generate revenue report"""
    payments = Payment.objects.select_related('registration__event')
    
    if event:
        payments = payments.filter(registration__event=event)
    if start_date:
        payments = payments.filter(created_at__gte=start_date)
    if end_date:
        payments = payments.filter(created_at__lte=end_date)
    
    total_revenue = payments.aggregate(total=Sum('amount'))['total'] or 0
    
    by_event = payments.values('registration__event__title').annotate(
        revenue=Sum('amount'),
        count=Count('id')
    ).order_by('-revenue')
    
    by_method = payments.values('payment_method').annotate(
        revenue=Sum('amount'),
        count=Count('id')
    )
    
    report = {
        'total_revenue': total_revenue,
        'total_transactions': payments.count(),
        'by_event': by_event,
        'by_method': by_method,
        'payments': payments.order_by('-created_at')
    }
    
    return report

def generate_attendance_report(event):
    """Generate attendance report for an event"""
    registrations = event.registrations.all()
    
    report = {
        'event': event,
        'total_capacity': event.capacity,
        'total_registered': registrations.count(),
        'total_paid': registrations.filter(payment_status=Registration.PAYMENT_COMPLETED).count(),
        'total_checked_in': registrations.filter(checked_in=True).count(),
        'available_seats': event.available_seats,
        'attendance_rate': 0,
        'registrations': registrations.order_by('attendee__username')
    }
    
    if report['total_paid'] > 0:
        report['attendance_rate'] = (report['total_checked_in'] / report['total_paid']) * 100
    
    return report
