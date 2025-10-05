from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta
from django.utils import timezone
from ckeditor_uploader.fields import RichTextUploadingField
import uuid

# ---------------------- Category ----------------------
class Category(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6c757d')  # Bootstrap secondary color
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Categories"
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def book_count(self):
        return self.books.count()  # related_name 'books' used in Book model

# ---------------------- Author ----------------------
class Author(models.Model):
    name = models.CharField(max_length=100, unique=True)
    bio = models.TextField(blank=True)
    date_of_birth = models.DateField(null=True, blank=True)
    date_of_death = models.DateField(null=True, blank=True)
    nationality = models.CharField(max_length=50, blank=True)
    website = models.URLField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

    @property
    def book_count(self):
        return self.books.count()

# ---------------------- Publisher ----------------------
class Publisher(models.Model):
    name = models.CharField(max_length=100, unique=True)
    address = models.TextField(blank=True)
    phone = models.CharField(max_length=15, blank=True)
    email = models.EmailField(blank=True)
    website = models.URLField(blank=True)
    established_year = models.PositiveIntegerField(
        null=True, blank=True,
        validators=[MinValueValidator(1000), MaxValueValidator(timezone.now().year)]
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name

# ---------------------- Book ----------------------
class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
        ('reserved', 'Reserved'),
        ('maintenance', 'Under Maintenance'),
        ('lost', 'Lost'),
    ]

    BOOK_TYPES = [
        ('hardcover', 'Hardcover'),
        ('paperback', 'Paperback'),
        ('ebook', 'E-Book'),
        ('audiobook', 'Audiobook'),
    ]

    title = models.CharField(max_length=200)
    subtitle = models.CharField(max_length=200, blank=True)
    authors = models.ManyToManyField(Author, related_name='books')
    isbn = models.CharField(max_length=13, unique=True, validators=[MinLengthValidator(10)], verbose_name='ISBN')
    isbn13 = models.CharField(max_length=17, unique=True, blank=True, null=True, verbose_name='ISBN-13')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)
    published_date = models.DateField(null=True, blank=True)
    edition = models.PositiveIntegerField(default=1)
    volume = models.PositiveIntegerField(null=True, blank=True)
    book_type = models.CharField(max_length=20, choices=BOOK_TYPES, default='hardcover')
    categories = models.ManyToManyField(Category, related_name='books', blank=True)
    language = models.CharField(max_length=20, default='English')
    page_count = models.PositiveIntegerField(null=True, blank=True)
    description = RichTextUploadingField(blank=True, null=True)
    summary = models.TextField(blank=True)
    keywords = models.CharField(max_length=200, blank=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    dimensions = models.CharField(max_length=50, blank=True)
    weight = models.DecimalField(max_digits=6, decimal_places=2, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    acquisition_date = models.DateField(default=timezone.now)
    acquisition_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.CharField(max_length=50, blank=True)
    barcode = models.CharField(max_length=50, unique=True, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='books_added')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['isbn']),
            models.Index(fields=['status']),
            models.Index(fields=['barcode']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.isbn13 and self.isbn:
            if len(self.isbn) == 10:
                self.isbn13 = f"978{self.isbn[:-1]}"
            else:
                self.isbn13 = self.isbn
        if not self.barcode:
            self.barcode = f"LIB{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    def author_names(self):
        return ", ".join([author.name for author in self.authors.all()])

    def category_names(self):
        return ", ".join([category.name for category in self.categories.all()])

    @property
    def is_available(self):
        return self.status == 'available'

    @property
    def is_overdue(self):
        if self.status == 'borrowed':
            latest_borrow = self.borrowrecord_set.filter(return_date__isnull=True).first()
            return latest_borrow.is_overdue() if latest_borrow else False
        return False

# ---------------------- Member (Merged) ----------------------
class Member(models.Model):
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    member_id = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    membership_date = models.DateField(auto_now_add=True)
    expiration_date = models.DateField(blank=True, null=True)
    fine_balance = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='guest')

    def save(self, *args, **kwargs):
        # Automatically set expiration 1 year from membership_date if not set
        if not self.expiration_date:
            self.expiration_date = self.membership_date + timedelta(days=365)
        super().save(*args, **kwargs)

    @property
    def is_membership_valid(self):
        if self.expiration_date:
            return self.expiration_date >= timezone.now().date()
        return False



# ---------------------- BorrowRecord ----------------------
class BorrowRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField()
    return_date = models.DateTimeField(null=True, blank=True)
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)

    def save(self, *args, **kwargs):
        if not self.due_date and not self.pk:
            self.due_date = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)

    def calculate_fine(self):
        if self.return_date and self.return_date > self.due_date:
            days_overdue = (self.return_date - self.due_date).days
            return days_overdue * 2.00
        return 0.00

    def __str__(self):
        return f"{self.member} borrowed {self.book}"

# ---------------------- Reservation ----------------------
class Reservation(models.Model):
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('fulfilled', 'Fulfilled'),
        ('cancelled', 'Cancelled'),
    ]

    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    reservation_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active')
    notification_sent = models.BooleanField(default=False)

    class Meta:
        unique_together = ['book', 'member']

    def __str__(self):
        return f"{self.member} reserved {self.book}"
