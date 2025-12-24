from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.mail import send_mail
from library_app.models import BorrowRecord

class Command(BaseCommand):
    help = 'Send email alerts for overdue borrowed books'

    def handle(self, *args, **options):
        overdue_borrows = BorrowRecord.objects.filter(
            return_date__isnull=True,
            due_date__lt=timezone.now()
        ).select_related('member__user', 'book')

        if not overdue_borrows:
            self.stdout.write('No overdue books found.')
            return

        for borrow in overdue_borrows:
            member = borrow.member
            user = member.user
            book = borrow.book
            days_overdue = (timezone.now().date() - borrow.due_date.date()).days

            subject = f'Overdue Book Alert: {book.title}'
            message = f"""
Dear {user.get_full_name() or user.username},

This is a reminder that the book "{book.title}" you borrowed is {days_overdue} days overdue.

Due Date: {borrow.due_date.date()}
Please return the book as soon as possible to avoid additional fines.

Thank you,
Library Management System
"""

            try:
                send_mail(
                    subject,
                    message,
                    'Library Management System <noreply@library.com>',  # Update with your email
                    [user.email],
                    fail_silently=False,
                )
                self.stdout.write(f'Sent alert to {user.email} for book "{book.title}"')
            except Exception as e:
                self.stderr.write(f'Failed to send email to {user.email}: {e}')

        self.stdout.write(f'Sent {len(overdue_borrows)} overdue alerts.')