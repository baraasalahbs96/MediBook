from django.core.management.base import BaseCommand
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from users_app.models import Appointment


class Command(BaseCommand):
    help = 'Send email reminders for appointments within the next 24 hours'

    def handle(self, *args, **options):
        now   = timezone.now()
        start = now + timedelta(hours=23)
        end   = now + timedelta(hours=25)

        appointments = Appointment.objects.filter(
            date__range=(start.date(), end.date()),
            reminder_sent=False,
            status__in=['pending', 'confirmed'],
        )

        count = 0
        for appt in appointments:
            try:
                send_mail(
                    subject='Appointment Reminder - MediBook',
                    message=(
                        f'Hi {appt.patient.first_name},\n\n'
                        f'This is a reminder for your appointment with Dr. {appt.doctor.name}.\n'
                        f'Date: {appt.date}\n'
                        f'Time: {appt.time}\n\n'
                        f'To cancel or reschedule, please contact the clinic.\n\n'
                        f'MediBook Team'
                    ),
                    from_email=settings.EMAIL_HOST_USER,
                    recipient_list=[appt.patient.email],
                    fail_silently=False,
                )
                appt.reminder_sent = True
                appt.save()
                count += 1
            except Exception as e:
                self.stdout.write(self.style.ERROR(f'Failed for {appt.patient.email}: {e}'))

        self.stdout.write(self.style.SUCCESS(f'Sent {count} reminder(s)'))