from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
import uuid

class UserProfile(models.Model):
    ROLE_ADMIN = 'admin'
    ROLE_ORGANIZER = 'organizer'
    ROLE_ATTENDEE = 'attendee'
    ROLE_CHOICES = [
        (ROLE_ADMIN, 'Admin'),
        (ROLE_ORGANIZER, 'Organizer'),
        (ROLE_ATTENDEE, 'Attendee'),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default=ROLE_ATTENDEE)
    phone = models.CharField(max_length=20, blank=True)
    def __str__(self):
        return f"{self.user.username} - {self.role}"

class Event(models.Model):
    STATUS_SCHEDULED = 'scheduled'
    STATUS_CANCELLED = 'cancelled'
    STATUS_COMPLETED = 'completed'
    STATUS_CHOICES = [
        (STATUS_SCHEDULED, 'Scheduled'),
        (STATUS_CANCELLED, 'Cancelled'),
        (STATUS_COMPLETED, 'Completed'),
    ]
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    date = models.DateField()
    time = models.TimeField(blank=True, null=True)
    location = models.CharField(max_length=250, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events', null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_SCHEDULED)
    capacity = models.PositiveIntegerField(default=100, validators=[MinValueValidator(1)])
    ticket_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    reminder_enabled = models.BooleanField(default=False)
    reminder_phone = models.CharField(max_length=20, blank=True)
    reminder_sent = models.BooleanField(default=False)
    REMINDER_CHANNEL_SMS = 'sms'
    REMINDER_CHANNEL_WHATSAPP = 'whatsapp'
    REMINDER_CHANNEL_EMAIL = 'email'
    REMINDER_CHANNEL_CHOICES = [
        (REMINDER_CHANNEL_SMS, 'SMS'),
        (REMINDER_CHANNEL_WHATSAPP, 'WhatsApp'),
        (REMINDER_CHANNEL_EMAIL, 'Email'),
    ]
    reminder_channel = models.CharField(max_length=10, choices=REMINDER_CHANNEL_CHOICES, default=REMINDER_CHANNEL_EMAIL)
    def __str__(self):
        return self.title
    @property
    def available_seats(self):
        registered = self.registrations.filter(payment_status='completed').count()
        return self.capacity - registered
    @property
    def is_full(self):
        return self.available_seats <= 0
    @property
    def total_revenue(self):
        from django.db.models import Sum
        result = self.registrations.filter(payment_status='completed').aggregate(total=Sum('amount_paid'))
        return result['total'] or 0

class Registration(models.Model):
    PAYMENT_PENDING = 'pending'
    PAYMENT_COMPLETED = 'completed'
    PAYMENT_FAILED = 'failed'
    PAYMENT_REFUNDED = 'refunded'
    PAYMENT_STATUS_CHOICES = [
        (PAYMENT_PENDING, 'Pending'),
        (PAYMENT_COMPLETED, 'Completed'),
        (PAYMENT_FAILED, 'Failed'),
        (PAYMENT_REFUNDED, 'Refunded'),
    ]
    event = models.ForeignKey(Event, on_delete=models.CASCADE, related_name='registrations')
    attendee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='registrations')
    registered_at = models.DateTimeField(auto_now_add=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default=PAYMENT_PENDING)
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    payment_id = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(null=True, blank=True)
    ticket_number = models.CharField(max_length=50, unique=True, blank=True)
    qr_code = models.TextField(blank=True)
    checked_in = models.BooleanField(default=False)
    checked_in_at = models.DateTimeField(null=True, blank=True)
    confirmation_sent = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    class Meta:
        unique_together = ['event', 'attendee']
    def __str__(self):
        return f"{self.attendee.username} - {self.event.title}"
    def save(self, *args, **kwargs):
        if not self.ticket_number:
            self.ticket_number = f"TKT-{uuid.uuid4().hex[:10].upper()}"
        super().save(*args, **kwargs)

class Payment(models.Model):
    PAYMENT_METHOD_CARD = 'card'
    PAYMENT_METHOD_UPI = 'upi'
    PAYMENT_METHOD_NETBANKING = 'netbanking'
    PAYMENT_METHOD_WALLET = 'wallet'
    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_CARD, 'Credit/Debit Card'),
        (PAYMENT_METHOD_UPI, 'UPI'),
        (PAYMENT_METHOD_NETBANKING, 'Net Banking'),
        (PAYMENT_METHOD_WALLET, 'Wallet'),
    ]
    registration = models.OneToOneField(Registration, on_delete=models.CASCADE, related_name='payment_detail')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES)
    transaction_id = models.CharField(max_length=100, unique=True)
    payment_gateway_response = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now=True)
    def __str__(self):
        return f"Payment {self.transaction_id} - {self.amount}"
