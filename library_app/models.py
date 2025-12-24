from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator, MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import timedelta, date
from ckeditor_uploader.fields import RichTextUploadingField
import uuid

# ---------------------- Category ----------------------
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    color = models.CharField(max_length=7, default='#6c757d')
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
        return self.books.count()

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

# ---------------------- Language ----------------------
class Language(models.Model):
    name = models.CharField(max_length=50, unique=True)

    def __str__(self):
        return self.name

# ---------------------- Location ----------------------
class Location(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.name

# ---------------------- Member ----------------------
class Member(models.Model):
    ROLE_CHOICES = [
        ('guest', 'Guest'),
        ('student', 'Student'),
        ('teacher', 'Teacher'),
        ('staff', 'Staff'),
        ('admin', 'Admin'),
        ('member', 'Member'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    member_id = models.CharField(max_length=10, unique=True)
    phone = models.CharField(max_length=15, blank=True)
    address = models.TextField(blank=True)
    membership_date = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    role = models.CharField(max_length=20, choices=ROLE_CHOICES, default='member')
    fine_balance = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    card_number = models.CharField(max_length=20, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.membership_date:
            self.membership_date = date.today()
        if not self.card_number:
            self.card_number = f"LIB{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def expiration_date(self):
        if self.membership_date:
            return self.membership_date + timedelta(days=365)
        return None

    @property
    def is_membership_valid(self):
        exp_date = self.expiration_date
        return exp_date >= timezone.now().date() if exp_date else False

    @property
    def can_borrow(self):
        # Staff and Admin can borrow without restrictions
        if self.role in ['staff', 'admin']:
            return True
        # Guests/students/teachers can borrow if active and membership valid
        return self.is_active and self.is_membership_valid

    @property
    def fine_balance_display(self):
        """Display the fine balance as a formatted string"""
        return f"{self.fine_balance:.2f}"

    def generate_library_card_image(self, format_type='code128', include_text=True, width=2, height=40):
        """Generate library card barcode image for the member with customizable options"""
        try:
            import barcode
            from barcode.writer import ImageWriter
            from io import BytesIO

            # Choose barcode format - QR codes are better for member cards
            if format_type.lower() == 'qr':
                # For QR codes, we could use qrcode library
                # For now, use Code 128 as fallback
                code_class = barcode.get_barcode_class('code128')
            else:
                code_class = barcode.get_barcode_class('code128')

            barcode_instance = code_class(self.card_number, writer=ImageWriter())

            # Generate barcode with enhanced options for library cards
            options = {
                'write_text': include_text,  # Include text for library cards
                'module_height': height / 3,  # Height of barcode bars
                'module_width': width / 8,    # Width of barcode bars
                'quiet_zone': 1.5,           # Space around barcode
                'font_size': 12 if include_text else 0,
                'text_distance': 3 if include_text else 0,
            }

            # Save to BytesIO
            buffer = BytesIO()
            barcode_instance.write(buffer, options=options)
            buffer.seek(0)

            return buffer.getvalue()

        except ImportError:
            raise Exception("Barcode generation library not available. Please install 'python-barcode'.")
        except Exception as e:
            raise Exception(f"Error generating library card barcode: {str(e)}")

    def get_library_card_data_url(self, format_type='code128', include_text=True):
        """Generate library card barcode and return as data URL"""
        try:
            import base64
            barcode_image = self.generate_library_card_image(format_type, include_text)
            encoded = base64.b64encode(barcode_image).decode('utf-8')
            return f"data:image/png;base64,{encoded}"
        except Exception as e:
            return None

    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} ({self.role})"

# ---------------------- Book ----------------------
class Book(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('borrowed', 'Borrowed'),
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
    isbn = models.CharField(max_length=13, unique=True, validators=[MinLengthValidator(10)])
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, blank=True)
    published_date = models.DateField(null=True, blank=True)
    edition = models.PositiveIntegerField(default=1)
    volume = models.PositiveIntegerField(null=True, blank=True)
    book_type = models.CharField(max_length=20, choices=BOOK_TYPES, default='hardcover')
    categories = models.ManyToManyField(Category, related_name='books', blank=True)
    page_count = models.PositiveIntegerField(null=True, blank=True)
    description = RichTextUploadingField(blank=True, null=True)
    cover_image = models.ImageField(
        upload_to='book_covers/',
        blank=True,
        null=True,
        help_text='Upload a cover image (JPG, PNG, GIF). Max size: 5MB'
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    available_copies = models.PositiveIntegerField(default=1)
    acquisition_date = models.DateField(default=timezone.now)
    acquisition_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, blank=True)
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='books_added')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    barcode = models.CharField(max_length=20, unique=True, blank=True)

    class Meta:
        ordering = ['title']
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['isbn']),
            models.Index(fields=['status']),
        ]
        permissions = [
            ("manage_books", "Can manage books (CRUD)"),
        ]

    def save(self, *args, **kwargs):
        if not self.barcode:
            self.barcode = f"LIB{uuid.uuid4().hex[:8].upper()}"
        super().save(*args, **kwargs)

    @property
    def is_available(self):
        return self.status == 'available' and self.available_copies > 0

    @property
    def author_names(self):
        return ', '.join([author.name for author in self.authors.all()])

    @property
    def category_names(self):
        return ', '.join([category.name for category in self.categories.all()])

    def generate_library_card_image(self):
        """Generate clean library card image for the member (no text below)"""
        try:
            import barcode
            from barcode.writer import ImageWriter
            from io import BytesIO

            # Use Code 128 barcode
            code128 = barcode.get_barcode_class('code128')
            barcode_instance = code128(self.card_number, writer=ImageWriter())

            # Generate barcode with custom options - clean style (no text)
            options = {
                'write_text': False,   # Remove human-readable text below barcode
                'module_height': 15.0, # Height of barcode bars
                'module_width': 0.5,   # Width of single bar
                'quiet_zone': 2.0,     # Space around barcode
            }

            # Save to BytesIO
            buffer = BytesIO()
            barcode_instance.write(buffer, options=options)
            buffer.seek(0)

            return buffer.getvalue()

        except Exception as e:
            raise Exception(f"Error generating barcode: {str(e)}")

    def borrow(self, member: Member):
        if not member.can_borrow:
            raise ValueError("Member cannot borrow books")

        # Check if member has already borrowed 3 books
        current_borrows = BorrowRecord.objects.filter(
            member=member,
            return_date__isnull=True
        ).count()
        if current_borrows >= 3:
            raise ValueError("Member has reached the maximum limit of 3 borrowed books")

        if self.is_available:
            self.available_copies -= 1
            if self.available_copies == 0:
                self.status = 'borrowed'
            self.save()
            return BorrowRecord.objects.create(book=self, member=member)
        else:
            raise ValueError("Book not available")

    def return_book(self, borrow_record: 'BorrowRecord'):
        if borrow_record.return_date:
            raise ValueError("Book already returned")
        borrow_record.return_date = timezone.now()
        borrow_record.save()
        self.available_copies += 1
        self.status = 'available'
        self.save()

    def generate_barcode_image(self, format_type='code128', include_text=False, width=2, height=60):
        """Generate barcode image for the book with customizable options"""
        try:
            import barcode
            from barcode.writer import ImageWriter
            from io import BytesIO

            # Choose barcode format
            if format_type.lower() == 'qr':
                # For QR codes, we'd need a different library like qrcode
                # For now, fall back to Code 128
                code_class = barcode.get_barcode_class('code128')
            else:
                code_class = barcode.get_barcode_class('code128')

            barcode_instance = code_class(self.barcode, writer=ImageWriter())

            # Generate barcode with enhanced options
            options = {
                'write_text': include_text,  # Option to include human-readable text
                'module_height': height / 4,  # Height of barcode bars (adjusted for total height)
                'module_width': width / 10,   # Width of single bar
                'quiet_zone': 1.0,           # Space around barcode
                'font_size': 10 if include_text else 0,
                'text_distance': 5 if include_text else 0,
            }

            # Save to BytesIO
            buffer = BytesIO()
            barcode_instance.write(buffer, options=options)
            buffer.seek(0)

            return buffer.getvalue()

        except ImportError:
            raise Exception("Barcode generation library not available. Please install 'python-barcode'.")
        except Exception as e:
            raise Exception(f"Error generating barcode: {str(e)}")

    def get_barcode_data_url(self, format_type='code128', include_text=False):
        """Generate barcode and return as data URL for embedding in HTML"""
        try:
            import base64
            barcode_image = self.generate_barcode_image(format_type, include_text)
            encoded = base64.b64encode(barcode_image).decode('utf-8')
            return f"data:image/png;base64,{encoded}"
        except Exception as e:
            return None

    def __str__(self):
        return self.title

# ---------------------- BorrowRecord ----------------------
class BorrowRecord(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='borrows')
    member = models.ForeignKey(Member, on_delete=models.CASCADE)
    borrow_date = models.DateTimeField(auto_now_add=True)
    due_date = models.DateTimeField(blank=True, null=True)
    return_date = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = [
            ("manage_borrows", "Can manage borrow/return"),
        ]

    def save(self, *args, **kwargs):
        if not self.due_date:
            self.due_date = timezone.now() + timedelta(days=14)
        super().save(*args, **kwargs)

    @property
    def fine_amount(self):
        if self.return_date and self.due_date and self.return_date > self.due_date:
            days_overdue = (self.return_date - self.due_date).days
            return days_overdue * 2.00
        return 0.00

    @property
    def is_overdue(self):
        return timezone.now() > self.due_date if self.due_date and not self.return_date else False

    def __str__(self):
        return f"{self.member} borrowed {self.book}"



