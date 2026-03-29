# Test User Credentials

## Server URL
http://127.0.0.1:8000/

## Test Users

### 1. Administrator Account
- **Username:** admin
- **Password:** admin123
- **Email:** admin@example.com
- **Role:** Administrator
- **Permissions:** 
  - Full system access
  - Manage all users and assign roles
  - View and manage all events
  - Monitor system activity
  - Access all reports

### 2. Organizer Account
- **Username:** testuser
- **Password:** test123
- **Email:** test@example.com
- **Role:** Event Organizer
- **Permissions:** 
  - Create, edit, and delete own events
  - View event participants and registrations
  - Generate reports for own events
  - Manage event capacity and pricing

### 3. Attendee/Participant Account
- **Username:** attendee
- **Password:** attendee123
- **Email:** attendee@example.com
- **Role:** Participant/User
- **Permissions:** 
  - Register and login
  - View and browse all events
  - Register for events
  - Make payments
  - View and print tickets
  - Update own profile

## Sample Events Created

1. **Tech Conference 2026**
   - Price: $99.99
   - Capacity: 200 seats
   - Location: Convention Center, NYC
   - Date: 30 days from today

2. **Music Festival**
   - Price: $75.00
   - Capacity: 500 seats
   - Location: Central Park, NYC
   - Date: 45 days from today

3. **Free Workshop: Python Basics**
   - Price: FREE
   - Capacity: 50 seats
   - Location: Community Center
   - Date: 15 days from today

## Quick Start Guide

### For Administrators (admin):
1. Login at http://127.0.0.1:8000/login/
2. Access User Management from dashboard
3. View and edit user roles
4. Monitor system activity
5. Activate/deactivate users
6. Delete users if needed
7. View all events and registrations
8. Generate system-wide reports

### For Organizers (testuser):
1. Login at http://127.0.0.1:8000/login/
2. Go to Dashboard to see your events
3. Click "Add Event" to create new events
4. Set capacity, pricing, and event details
5. View registrations for each event
6. Generate reports from the Reports page
7. Track revenue and attendance

### For Attendees/Participants (attendee):
1. Login at http://127.0.0.1:8000/login/
2. Browse events at http://127.0.0.1:8000/events/
3. Click on an event to see details
4. Register for events
5. Complete payment (simulated)
6. View your tickets at "My Tickets"
7. Update your profile

## Features to Test

### User Management (Admin Only)
- View all users with filtering by role
- Search users by username, email, or name
- Edit user roles (Admin/Organizer/Attendee)
- Activate/Deactivate user accounts
- Delete users
- Monitor system activity log

### Role-Based Access Control
- Admin: Full access to all features
- Organizer: Event management and reports
- Attendee: Event browsing and registration

### Registration & Ticketing
- Register for free events (instant confirmation)
- Register for paid events (payment flow)
- View digital tickets
- Print tickets

### Event Management (Organizer)
- Create events with capacity and pricing
- Edit event details
- Cancel events (change status)
- View real-time seat availability
- Track registrations

### Reports (Organizer)
- Registration Report: See all registrations and payment status
- Revenue Report: Track earnings by event
- Attendance Report: Monitor check-ins and attendance rates

### Notifications
- Email confirmations (check console output in development)
- SMS/WhatsApp reminders (if Twilio configured)

## Admin Panel
Access Django admin at: http://127.0.0.1:8000/admin/
- Create superuser if needed: `python manage.py createsuperuser`

## Notes
- Payment gateway is simulated for demonstration
- Email notifications appear in console (development mode)
- All features are fully functional
- Database: SQLite (db.sqlite3)
