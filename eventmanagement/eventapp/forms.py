from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Event, Registration, UserProfile

class RegisterForm(UserCreationForm):
    email = forms.EmailField(
        required=True,
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Enter your email'})
    )
    first_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your first name'})
    )
    last_name = forms.CharField(
        max_length=30,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter your last name'})
    )
    phone = forms.CharField(
        max_length=20,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1234567890'})
    )
    role = forms.ChoiceField(
        choices=UserProfile.ROLE_CHOICES,
        initial=UserProfile.ROLE_ATTENDEE,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Choose a username'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Create a strong password'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Confirm your password'
        })
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        if commit:
            user.save()
            # Update profile with role and phone
            user.profile.role = self.cleaned_data['role']
            user.profile.phone = self.cleaned_data.get('phone', '')
            user.profile.save()
        return user

class LoginForm(AuthenticationForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['username'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your username'
        })
        self.fields['password'].widget.attrs.update({
            'class': 'form-control',
            'placeholder': 'Enter your password'
        })

class EventForm(forms.ModelForm):
    class Meta:
        model = Event
        fields = ['title', 'description', 'date', 'time', 'location', 'capacity', 'ticket_price', 
                  'status', 'reminder_enabled', 'reminder_phone', 'reminder_channel']
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control shadow-sm'}),
            'description': forms.Textarea(attrs={'class': 'form-control shadow-sm', 'rows': 4}),
            'date': forms.DateInput(attrs={'class': 'form-control shadow-sm', 'type': 'date'}),
            'time': forms.TimeInput(attrs={'class': 'form-control shadow-sm', 'type': 'time'}),
            'location': forms.TextInput(attrs={'class': 'form-control shadow-sm'}),
            'capacity': forms.NumberInput(attrs={'class': 'form-control shadow-sm', 'min': 1}),
            'ticket_price': forms.NumberInput(attrs={'class': 'form-control shadow-sm', 'step': '0.01', 'min': 0}),
            'status': forms.Select(attrs={'class': 'form-select shadow-sm'}),
            'reminder_phone': forms.TextInput(attrs={'class': 'form-control shadow-sm', 'placeholder': '+15551234567'}),
            'reminder_channel': forms.Select(attrs={'class': 'form-select shadow-sm'}),
        }

class RegistrationForm(forms.ModelForm):
    class Meta:
        model = Registration
        fields = []
    
    def __init__(self, *args, **kwargs):
        self.event = kwargs.pop('event', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
    
    def clean(self):
        cleaned_data = super().clean()
        if self.event and self.event.is_full:
            raise forms.ValidationError("This event is fully booked.")
        if self.event and self.event.status != Event.STATUS_SCHEDULED:
            raise forms.ValidationError("This event is not available for registration.")
        return cleaned_data

class PaymentForm(forms.Form):
    PAYMENT_METHOD_CHOICES = [
        ('card', 'Credit/Debit Card'),
        ('upi', 'UPI'),
        ('netbanking', 'Net Banking'),
        ('wallet', 'Wallet'),
    ]
    
    payment_method = forms.ChoiceField(
        choices=PAYMENT_METHOD_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    
    # Card details (conditional)
    card_number = forms.CharField(
        max_length=16,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '1234 5678 9012 3456'})
    )
    card_expiry = forms.CharField(
        max_length=5,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'MM/YY'})
    )
    card_cvv = forms.CharField(
        max_length=3,
        required=False,
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'placeholder': 'CVV'})
    )
    
    # UPI details
    upi_id = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'yourname@upi'})
    )



