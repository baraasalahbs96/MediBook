from django.core.management.base import BaseCommand
from datetime import date, timedelta
from bookings.models import Appointment

class Command(BaseCommand):
    help = "Send appointment reminders"

    def handle(self, *args, **kwargs):
        tomorrow = date.today() + timedelta(days=1)

        appointments = Appointment.objects.filter(
            date=tomorrow
        )

        for appointment in appointments:
            print(
                f"Reminder sent to {appointment.patient}"
            )

        self.stdout.write(
            self.style.SUCCESS(
                "Reminders completed"
            )
        )