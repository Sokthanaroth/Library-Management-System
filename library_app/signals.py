from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Book, Reservation
from .utils import send_reservation_available

@receiver(post_save, sender=Book)
def handle_book_status_change(sender, instance, **kwargs):
    """
    When a book status changes to available, check if there are reservations
    and notify the first person in the queue
    """
    if instance.status == 'available':
        # Check if there are active reservations for this book
        reservation = Reservation.objects.filter(
            book=instance, 
            status='active'
        ).order_by('reservation_date').first()
        
        if reservation:
            # Notify the member
            send_reservation_available(reservation)
            # Update reservation status
            reservation.status = 'fulfilled'
            reservation.save()