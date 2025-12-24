from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Book

# No reservation signals needed since reservations are removed