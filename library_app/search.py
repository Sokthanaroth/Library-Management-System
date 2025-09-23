from .models import Book
from django.db.models import Q

def advanced_book_search(query='', filters={}):
    books = Book.objects.all()

    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(author__icontains=query) |
            Q(description__icontains=query)
        )

    if 'status' in filters:
        books = books.filter(status=filters['status'])
    if 'category' in filters:
        books = books.filter(category=filters['category'])
    if 'year' in filters:
        books = books.filter(year=filters['year'])

    return books
