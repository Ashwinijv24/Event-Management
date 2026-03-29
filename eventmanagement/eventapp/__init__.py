def send_sms(to_number: str, message: str) -> None:
    from django.conf import settings
    try:
        from twilio.rest import Client
    except Exception:
        return

    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    from_number = getattr(settings, 'TWILIO_FROM_NUMBER', None)
    if not all([account_sid, auth_token, from_number, to_number, message]):
        return

    client = Client(account_sid, auth_token)
    client.messages.create(body=message, from_=from_number, to=to_number)

def send_whatsapp(to_number: str, message: str) -> None:
    from django.conf import settings
    try:
        from twilio.rest import Client
    except Exception:
        return

    account_sid = getattr(settings, 'TWILIO_ACCOUNT_SID', None)
    auth_token = getattr(settings, 'TWILIO_AUTH_TOKEN', None)
    from_number = getattr(settings, 'TWILIO_WHATSAPP_FROM', None)
    if not all([account_sid, auth_token, from_number, to_number, message]):
        return

    client = Client(account_sid, auth_token)
    # Twilio WhatsApp requires numbers prefixed with 'whatsapp:'
    client.messages.create(body=message, from_=f"whatsapp:{from_number}", to=f"whatsapp:{to_number}")

