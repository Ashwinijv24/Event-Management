from django.apps import AppConfig
import os
class EventappConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'eventapp'
    def ready(self):
        # Import signals
        import eventapp.signals
        
        # Lazy import to avoid side effects during migrations
        from apscheduler.schedulers.background import BackgroundScheduler
        from django.utils import timezone
        from django.conf import settings
        from .models import Event
        from . import send_sms, send_whatsapp

        # Avoid starting multiple schedulers in autoreload
        if settings.DEBUG and os.environ.get('RUN_MAIN') != 'true':
            return

        scheduler = BackgroundScheduler(timezone=str(timezone.get_current_timezone()))

        def send_due_reminders():
            now = timezone.now()
            from django.db.models import Q
            # Event datetime combines date + time; if no time, assume 09:00 local
            default_hour = 9
            events = Event.objects.filter(
                reminder_enabled=True,
                reminder_sent=False,
                date__lte=now.date()
            )
            for ev in events:
                if not ev.reminder_phone:
                    continue
                if ev.time:
                    from datetime import datetime
                    event_dt = timezone.make_aware(datetime.combine(ev.date, ev.time))
                else:
                    from datetime import datetime, time as dtime
                    event_dt = timezone.make_aware(datetime.combine(ev.date, dtime(hour=default_hour)))
                # Send when event time has passed but not yet marked sent
                if event_dt <= now:
                    try:
                        msg = f"Reminder: '{ev.title}' is scheduled now at {ev.location or 'your calendar'}."
                        if getattr(ev, 'reminder_channel', 'sms') == 'whatsapp':
                            send_whatsapp(ev.reminder_phone, msg)
                        else:
                            send_sms(ev.reminder_phone, msg)
                        ev.reminder_sent = True
                        ev.save(update_fields=['reminder_sent'])
                    except Exception:
                        # swallow to keep scheduler alive
                        pass

        try:
            scheduler.add_job(send_due_reminders, 'interval', minutes=1, id='eventapp_send_due_reminders', replace_existing=True)
            scheduler.start()
        except Exception:
            # In case scheduler fails (e.g., during tests), ignore
            pass
