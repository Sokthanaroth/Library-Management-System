from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

def send_library_email(subject, template_name, context, recipient_list):
    """
    Send email using a template
    """
    html_message = render_to_string(template_name, context)
    plain_message = strip_tags(html_message)
    
    send_mail(
        subject,
        plain_message,
        settings.DEFAULT_FROM_EMAIL,
        recipient_list,
        html_message=html_message,
        fail_silently=False,
    )

def send_due_date_reminder(borrow_record):
    """
    Send reminder email about due date
    """
    subject = f'Reminder: Book Due Date Approaching - {borrow_record.book.title}'
    template_name = 'library_app/emails/due_date_reminder.html'
    
    context = {
        'member': borrow_record.member,
        'book': borrow_record.book,
        'borrow_record': borrow_record,
    }
    
    recipient_list = [borrow_record.member.user.email]
    send_library_email(subject, template_name, context, recipient_list)
