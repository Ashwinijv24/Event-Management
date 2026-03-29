from django.contrib import admin
from .models import Event, UserProfile, Registration, Payment

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'phone')
    list_filter = ('role',)
    search_fields = ('user__username', 'user__email', 'phone')

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('title', 'date', 'time', 'location', 'status', 'capacity', 'ticket_price', 'created_by', 'created_at')
    list_filter = ('date', 'status', 'created_by')
    search_fields = ('title', 'description', 'location')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ('ticket_number', 'event', 'attendee', 'payment_status', 'amount_paid', 'registered_at', 'checked_in')
    list_filter = ('payment_status', 'checked_in', 'registered_at')
    search_fields = ('ticket_number', 'attendee__username', 'event__title')
    readonly_fields = ('ticket_number', 'registered_at')

@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ('transaction_id', 'registration', 'amount', 'payment_method', 'created_at')
    list_filter = ('payment_method', 'created_at')
    search_fields = ('transaction_id', 'registration__ticket_number')
    readonly_fields = ('created_at',)
