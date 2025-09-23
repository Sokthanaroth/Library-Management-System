from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta
from library_app.models import BorrowRecord
from library_app.utils import send_due_date_reminder

class Command(BaseCommand):
    help = 'Send due date reminder emails for books due in 2 days'
    
    def handle(self, *args, **options):
        # Find books due in 2 days that haven't been returned
        two_days_from_now = timezone.now() + timedelta(days=2)
        borrow_records = BorrowRecord.objects.filter(
            due_date__lte=two_days_from_now,
            return_date__isnull=True
        )
        
        for record in borrow_records:
            try:
                send_due_date_reminder(record)
                self.stdout.write(
                    self.style.SUCCESS(f'Sent reminder for {record.book.title} to {record.member.user.email}')
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Failed to send reminder for {record.book.title}: {str(e)}')
                )