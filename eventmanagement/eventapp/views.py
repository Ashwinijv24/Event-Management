from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from django.db.models import Q, Sum, Count
from django.http import HttpResponse, JsonResponse
from .forms import RegisterForm, LoginForm, EventForm, RegistrationForm, PaymentForm
from .models import Event, Registration, Payment, UserProfile
from .utils import send_confirmation_email, generate_registration_report, generate_revenue_report, generate_attendance_report
import uuid
from datetime import datetime, timedelta

def home(request):
    events = Event.objects.filter(
        status=Event.STATUS_SCHEDULED,
        date__gte=timezone.now().date()
    ).order_by('date')[:6]
    return render(request, 'eventapp/index.html', {'events': events})

def register_view(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = RegisterForm()
    return render(request, 'eventapp/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            messages.success(request, 'Login successful!')
            return redirect('home')
    else:
        form = LoginForm()
    return render(request, 'eventapp/login.html', {'form': form})

def logout_view(request):
    logout(request)
    messages.info(request, 'Logged out successfully.')
    return redirect('login')

@login_required
def dashboard(request):
    user_role = request.user.profile.role
    
    if user_role == UserProfile.ROLE_ORGANIZER or user_role == UserProfile.ROLE_ADMIN:
        events = Event.objects.filter(created_by=request.user).order_by('-created_at')
        context = {
            'events': events,
            'total_events': events.count(),
            'total_registrations': Registration.objects.filter(event__created_by=request.user).count(),
            'total_revenue': Registration.objects.filter(
                event__created_by=request.user,
                payment_status=Registration.PAYMENT_COMPLETED
            ).aggregate(total=Sum('amount_paid'))['total'] or 0,
        }
    else:
        registrations = Registration.objects.filter(attendee=request.user).select_related('event')
        context = {
            'registrations': registrations,
            'upcoming_events': registrations.filter(
                event__date__gte=timezone.now().date(),
                event__status=Event.STATUS_SCHEDULED
            ).count(),
        }
    
    context['user_role'] = user_role
    return render(request, 'eventapp/dashboard.html', context)

@login_required
def add_event(request):
    if request.user.profile.role not in [UserProfile.ROLE_ORGANIZER, UserProfile.ROLE_ADMIN]:
        messages.error(request, 'Only organizers can create events.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            ev = form.save(commit=False)
            ev.created_by = request.user
            ev.save()
            messages.success(request, 'Event created successfully.')
            return redirect('dashboard')
    else:
        form = EventForm()
    return render(request, 'eventapp/add_event.html', {'form': form})

@login_required
def edit_event(request, event_id):
    ev = get_object_or_404(Event, id=event_id)
    
    if ev.created_by != request.user and request.user.profile.role != UserProfile.ROLE_ADMIN:
        messages.error(request, 'You do not have permission to edit this event.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        form = EventForm(request.POST, instance=ev)
        if form.is_valid():
            form.save()
            messages.success(request, 'Event updated successfully.')
            return redirect('view_events')
    else:
        form = EventForm(instance=ev)
    return render(request, 'eventapp/edit_event.html', {'form': form, 'event': ev})

@login_required
def delete_event(request, event_id):
    ev = get_object_or_404(Event, id=event_id)
    
    if ev.created_by != request.user and request.user.profile.role != UserProfile.ROLE_ADMIN:
        messages.error(request, 'You do not have permission to delete this event.')
        return redirect('dashboard')
    
    if request.method == 'POST':
        ev.delete()
        messages.success(request, 'Event deleted successfully.')
        return redirect('view_events')
    return render(request, 'eventapp/delete_confirm.html', {'event': ev})

def view_events(request):
    events = Event.objects.filter(
        status=Event.STATUS_SCHEDULED,
        date__gte=timezone.now().date()
    ).order_by('date')
    
    # Filter by search query
    search = request.GET.get('search', '')
    if search:
        events = events.filter(
            Q(title__icontains=search) | 
            Q(description__icontains=search) |
            Q(location__icontains=search)
        )
    
    return render(request, 'eventapp/view_events.html', {'events': events, 'search': search})

@login_required
def event_detail(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    user_registered = Registration.objects.filter(event=event, attendee=request.user).exists()
    
    context = {
        'event': event,
        'user_registered': user_registered,
        'available_seats': event.available_seats,
    }
    return render(request, 'eventapp/event_detail.html', context)

@login_required
def register_for_event(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if event.status != Event.STATUS_SCHEDULED:
        messages.error(request, 'This event is not available for registration.')
        return redirect('event_detail', event_id=event_id)
    
    if event.is_full:
        messages.error(request, 'This event is fully booked.')
        return redirect('event_detail', event_id=event_id)
    
    if Registration.objects.filter(event=event, attendee=request.user).exists():
        messages.warning(request, 'You are already registered for this event.')
        return redirect('event_detail', event_id=event_id)
    
    if request.method == 'POST':
        # Create registration
        registration = Registration.objects.create(
            event=event,
            attendee=request.user,
            amount_paid=event.ticket_price
        )
        
        if event.ticket_price > 0:
            # Redirect to payment
            return redirect('payment', registration_id=registration.id)
        else:
            # Free event - mark as completed
            registration.payment_status = Registration.PAYMENT_COMPLETED
            registration.payment_date = timezone.now()
            registration.save()
            send_confirmation_email(registration)
            messages.success(request, 'Registration successful! Check your email for confirmation.')
            return redirect('my_tickets')
    
    return render(request, 'eventapp/register_confirm.html', {'event': event})

@login_required
def payment(request, registration_id):
    registration = get_object_or_404(Registration, id=registration_id, attendee=request.user)
    
    if registration.payment_status == Registration.PAYMENT_COMPLETED:
        messages.info(request, 'Payment already completed.')
        return redirect('my_tickets')
    
    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            # Simulate payment processing
            transaction_id = f"TXN-{uuid.uuid4().hex[:12].upper()}"
            
            # Create payment record
            payment = Payment.objects.create(
                registration=registration,
                amount=registration.amount_paid,
                payment_method=form.cleaned_data['payment_method'],
                transaction_id=transaction_id,
                payment_gateway_response="Payment successful (simulated)"
            )
            
            # Update registration
            registration.payment_status = Registration.PAYMENT_COMPLETED
            registration.payment_id = transaction_id
            registration.payment_date = timezone.now()
            registration.save()
            
            # Send confirmation
            send_confirmation_email(registration)
            
            messages.success(request, 'Payment successful! Your ticket has been generated.')
            return redirect('ticket_view', registration_id=registration.id)
    else:
        form = PaymentForm()
    
    context = {
        'registration': registration,
        'form': form,
    }
    return render(request, 'eventapp/payment.html', context)

@login_required
def my_tickets(request):
    registrations = Registration.objects.filter(
        attendee=request.user,
        payment_status=Registration.PAYMENT_COMPLETED
    ).select_related('event').order_by('-registered_at')
    
    return render(request, 'eventapp/my_tickets.html', {'registrations': registrations})

@login_required
def ticket_view(request, registration_id):
    registration = get_object_or_404(
        Registration,
        id=registration_id,
        attendee=request.user,
        payment_status=Registration.PAYMENT_COMPLETED
    )
    return render(request, 'eventapp/ticket.html', {'registration': registration})

@login_required
def event_registrations(request, event_id):
    event = get_object_or_404(Event, id=event_id)
    
    if event.created_by != request.user and request.user.profile.role != UserProfile.ROLE_ADMIN:
        messages.error(request, 'You do not have permission to view registrations.')
        return redirect('dashboard')
    
    registrations = event.registrations.select_related('attendee').order_by('-registered_at')
    
    context = {
        'event': event,
        'registrations': registrations,
        'total_registered': registrations.count(),
        'total_paid': registrations.filter(payment_status=Registration.PAYMENT_COMPLETED).count(),
        'total_revenue': registrations.filter(payment_status=Registration.PAYMENT_COMPLETED).aggregate(
            total=Sum('amount_paid')
        )['total'] or 0,
    }
    return render(request, 'eventapp/event_registrations.html', context)

@login_required
def reports(request):
    if request.user.profile.role not in [UserProfile.ROLE_ORGANIZER, UserProfile.ROLE_ADMIN]:
        messages.error(request, 'You do not have permission to view reports.')
        return redirect('dashboard')
    
    report_type = request.GET.get('type', 'registration')
    event_id = request.GET.get('event')
    
    events = Event.objects.filter(created_by=request.user)
    selected_event = None
    
    if event_id:
        selected_event = get_object_or_404(Event, id=event_id, created_by=request.user)
    
    if report_type == 'registration':
        report_data = generate_registration_report(event=selected_event)
    elif report_type == 'revenue':
        report_data = generate_revenue_report(event=selected_event)
    elif report_type == 'attendance' and selected_event:
        report_data = generate_attendance_report(selected_event)
    else:
        report_data = {}
    
    context = {
        'report_type': report_type,
        'report_data': report_data,
        'events': events,
        'selected_event': selected_event,
    }
    return render(request, 'eventapp/reports.html', context)


# Admin Views
from .decorators import admin_required, organizer_or_admin_required
from django.contrib.auth.models import User

@admin_required
def manage_users(request):
    """Admin view to manage all users"""
    users = User.objects.select_related('profile').order_by('-date_joined')
    
    # Filter by role if specified
    role_filter = request.GET.get('role')
    if role_filter:
        users = users.filter(profile__role=role_filter)
    
    # Search functionality
    search = request.GET.get('search')
    if search:
        users = users.filter(
            Q(username__icontains=search) |
            Q(email__icontains=search) |
            Q(first_name__icontains=search) |
            Q(last_name__icontains=search)
        )
    
    context = {
        'users': users,
        'total_users': User.objects.count(),
        'total_admins': User.objects.filter(profile__role='admin').count(),
        'total_organizers': User.objects.filter(profile__role='organizer').count(),
        'total_attendees': User.objects.filter(profile__role='attendee').count(),
        'role_filter': role_filter,
        'search': search,
    }
    return render(request, 'eventapp/manage_users.html', context)

@admin_required
def edit_user_role(request, user_id):
    """Admin view to edit user role"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        new_role = request.POST.get('role')
        if new_role in ['admin', 'organizer', 'attendee']:
            user.profile.role = new_role
            user.profile.save()
            messages.success(request, f'User role updated to {new_role}.')
        else:
            messages.error(request, 'Invalid role selected.')
        return redirect('manage_users')
    
    context = {'user': user}
    return render(request, 'eventapp/edit_user_role.html', context)

@admin_required
def toggle_user_status(request, user_id):
    """Admin view to activate/deactivate user"""
    user = get_object_or_404(User, id=user_id)
    
    if request.method == 'POST':
        user.is_active = not user.is_active
        user.save()
        status = 'activated' if user.is_active else 'deactivated'
        messages.success(request, f'User {user.username} has been {status}.')
    
    return redirect('manage_users')

@admin_required
def delete_user(request, user_id):
    """Admin view to delete user"""
    user = get_object_or_404(User, id=user_id)
    
    if user == request.user:
        messages.error(request, 'You cannot delete your own account.')
        return redirect('manage_users')
    
    if request.method == 'POST':
        username = user.username
        user.delete()
        messages.success(request, f'User {username} has been deleted.')
        return redirect('manage_users')
    
    context = {'user': user}
    return render(request, 'eventapp/delete_user_confirm.html', context)

@admin_required
def activity_log(request):
    """Admin view to monitor system activity"""
    # Get recent registrations
    recent_registrations = Registration.objects.select_related('event', 'attendee').order_by('-registered_at')[:20]
    
    # Get recent events
    recent_events = Event.objects.select_related('created_by').order_by('-created_at')[:20]
    
    # Get recent users
    recent_users = User.objects.select_related('profile').order_by('-date_joined')[:20]
    
    context = {
        'recent_registrations': recent_registrations,
        'recent_events': recent_events,
        'recent_users': recent_users,
    }
    return render(request, 'eventapp/activity_log.html', context)

@login_required
def user_profile(request):
    """View and edit user profile"""
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', '')
        user.last_name = request.POST.get('last_name', '')
        user.email = request.POST.get('email', '')
        user.save()
        
        user.profile.phone = request.POST.get('phone', '')
        user.profile.save()
        
        messages.success(request, 'Profile updated successfully.')
        return redirect('user_profile')
    
    return render(request, 'eventapp/user_profile.html')
