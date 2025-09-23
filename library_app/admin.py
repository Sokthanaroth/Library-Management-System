from django.contrib import admin
from .models import Book, Member, BorrowRecord, Reservation, Author, Category, Publisher

@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    # Display methods for ManyToMany fields
    list_display = ['title', 'display_authors', 'isbn', 'status', 'published_date']
    list_filter = ['status', 'categories', 'published_date']
    search_fields = ['title', 'isbn', 'authors__name']
    ordering = ['title']
    filter_horizontal = ('authors', 'categories')  # nice M2M widget

    # Method to show authors as comma-separated string
    def display_authors(self, obj):
        return ", ".join([author.name for author in obj.authors.all()])
    display_authors.short_description = 'Authors'


@admin.register(Member)
class MemberAdmin(admin.ModelAdmin):
    list_display = ['user', 'member_id', 'phone', 'membership_date', 'is_active']
    list_filter = ['is_active', 'membership_date']
    search_fields = ['user__first_name', 'user__last_name', 'member_id', 'phone']
    ordering = ['user__last_name']


@admin.register(BorrowRecord)
class BorrowRecordAdmin(admin.ModelAdmin):
    list_display = ['book', 'member', 'borrow_date', 'due_date', 'return_date', 'fine_amount']
    list_filter = ['borrow_date', 'due_date', 'return_date']
    search_fields = ['book__title', 'member__user__first_name', 'member__user__last_name']
    date_hierarchy = 'borrow_date'


@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ['book', 'member', 'reservation_date', 'status']
    list_filter = ['status', 'reservation_date']
    search_fields = ['book__title', 'member__user__first_name']
    ordering = ['-reservation_date']


# Optional: register other models
admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Publisher)
