from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm, PasswordChangeForm
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from .models import Book, Author, Publisher, Category, Member, BorrowRecord, Reservation
import json

# ---------------------- Category Form ----------------------
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'placeholder': 'Enter category name'}),
            'description': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Enter category description'}),
            'color': forms.TextInput(attrs={'type': 'color'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs.update({'class': 'form-control'})

# ---------------------- Book Form (Single Book) ----------------------
class BookForm(forms.ModelForm):
    new_authors = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Author1, Author2, Author3...',
            'class': 'form-control'
        }),
        help_text="Enter multiple authors separated by commas"
    )
    
    new_publisher = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Publisher name',
            'class': 'form-control'
        }),
        help_text="Create new publisher if not in list"
    )
    
    class Meta:
        model = Book
        fields = [
            'title', 'subtitle', 'isbn', 'published_date', 'edition', 'volume',
            'book_type', 'language', 'page_count', 'description', 'summary',
            'keywords', 'cover_image', 'dimensions', 'weight',
            'acquisition_price', 'location', 'categories'
        ]
        widgets = {
            'published_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'description': forms.Textarea(attrs={'rows': 4, 'class': 'form-control'}),
            'summary': forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}),
            'title': forms.TextInput(attrs={'class': 'form-control'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'edition': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'language': forms.TextInput(attrs={'class': 'form-control'}),
            'page_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'keywords': forms.TextInput(attrs={'class': 'form-control'}),
            'dimensions': forms.TextInput(attrs={'class': 'form-control'}),
            'weight': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'acquisition_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'categories': forms.CheckboxSelectMultiple(),
        }
        labels = {
            'isbn': 'ISBN (10 or 13 digits)',
            'acquisition_price': 'Acquisition Price ($)',
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['categories'].queryset = Category.objects.filter(is_active=True)
        
    def clean_isbn(self):
        isbn = self.cleaned_data.get('isbn', '').replace('-', '').replace(' ', '')
        if len(isbn) not in [10, 13]:
            raise forms.ValidationError("ISBN must be 10 or 13 digits long.")
        return isbn
    
    def save(self, commit=True, user=None):
        instance = super().save(commit=False)
        
        if user:
            instance.created_by = user
        
        # Handle new authors
        new_authors = self.cleaned_data.get('new_authors', '')
        if new_authors:
            author_names = [name.strip() for name in new_authors.split(',') if name.strip()]
            for name in author_names:
                author, created = Author.objects.get_or_create(name=name)
                if commit:
                    instance.save()
                    instance.authors.add(author)
        
        # Handle new publisher
        new_publisher = self.cleaned_data.get('new_publisher', '').strip()
        if new_publisher:
            publisher, created = Publisher.objects.get_or_create(name=new_publisher)
            instance.publisher = publisher
        
        if commit:
            instance.save()
            self.save_m2m()
        
        return instance

# ---------------------- Bulk Book Form ----------------------
class BulkBookForm(forms.Form):
    book_data = forms.CharField(
        widget=forms.Textarea(attrs={
            'rows': 10,
            'class': 'form-control',
            'placeholder': 'Enter book data in JSON format or one book per line with title, author, ISBN separated by pipes (|)'
        }),
        help_text="Format: Title | Author | ISBN | Publisher (optional)"
    )
    
    def clean_book_data(self):
        data = self.cleaned_data['book_data']
        lines = data.strip().split('\n')
        books = []
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            if not line:
                continue
                
            # Try JSON format first
            if line.startswith('{'):
                try:
                    book_info = json.loads(line)
                    books.append(book_info)
                except json.JSONDecodeError:
                    raise forms.ValidationError(f"Line {i}: Invalid JSON format")
            else:
                # Try pipe-separated format
                parts = [part.strip() for part in line.split('|')]
                if len(parts) < 3:
                    raise forms.ValidationError(f"Line {i}: Expected format: Title | Author | ISBN | Publisher (optional)")
                
                book_info = {
                    'title': parts[0],
                    'author': parts[1],
                    'isbn': parts[2],
                    'publisher': parts[3] if len(parts) > 3 else ''
                }
                books.append(book_info)
        
        return books

# ---------------------- ISBN Lookup Form ----------------------
class ISBNLookupForm(forms.Form):
    isbn = forms.CharField(
        max_length=13,
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter ISBN (10 or 13 digits)'
        })
    )
    
    def clean_isbn(self):
        isbn = self.cleaned_data['isbn'].replace('-', '').replace(' ', '')
        if len(isbn) not in [10, 13]:
            raise forms.ValidationError("ISBN must be 10 or 13 digits long.")
        return isbn

# ---------------------- CSV Upload Form ----------------------
class CSVUploadForm(forms.Form):
    csv_file = forms.FileField(
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.csv'
        }),
        help_text="Upload CSV file with columns: title, author, isbn, publisher, published_date, categories"
    )

# ---------------------- Member Form ----------------------
class MemberForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    email = forms.EmailField(required=True)
    
    class Meta:
        model = Member
        fields = ['member_id', 'phone', 'address']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

# ---------------------- Borrow Record Form ----------------------
class BorrowRecordForm(forms.ModelForm):
    class Meta:
        model = BorrowRecord
        fields = ['book', 'member', 'due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

# ---------------------- Reservation Form ----------------------
class ReservationForm(forms.ModelForm):
    class Meta:
        model = Reservation
        fields = ['book', 'member']

# ---------------------- User Registration Form ----------------------
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']

# ---------------------- User Update Form ----------------------
class UserUpdateForm(UserChangeForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=30, required=True)
    last_name = forms.CharField(max_length=30, required=True)
    
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Remove the password field
        self.fields.pop('password', None)

# ---------------------- Member Update Form ----------------------
class MemberUpdateForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['phone', 'address', ]
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 3}),
        }