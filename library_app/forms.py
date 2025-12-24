from django import forms
from django.contrib.auth.forms import UserCreationForm, UserChangeForm
from django.contrib.auth.models import User
from django.core.validators import MinLengthValidator
from datetime import datetime
from .models import (
    Book, Author, Location, Publisher, Category, Member,
    BorrowRecord, Language
)

# ---------------------- Category Form ----------------------
class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name', 'description', 'color']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter category name'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter description'}),
            'color': forms.TextInput(attrs={'type': 'color', 'class': 'form-control'}),
        }

# ---------------------- Author Form ----------------------
class AuthorForm(forms.ModelForm):
    class Meta:
        model = Author
        fields = ['name', 'bio', 'date_of_birth', 'date_of_death', 'nationality', 'website']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'date_of_birth': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'date_of_death': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'nationality': forms.TextInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name').strip()
        # Exclude current instance when updating
        queryset = Author.objects.filter(name__iexact=name)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("Author with this name already exists.")
        return name

# ---------------------- Publisher Form ----------------------
class PublisherForm(forms.ModelForm):
    class Meta:
        model = Publisher
        fields = ['name', 'address', 'phone', 'email', 'website', 'established_year']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Publisher name'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'website': forms.URLInput(attrs={'class': 'form-control'}),
            'established_year': forms.NumberInput(attrs={'class': 'form-control', 'min': 1000, 'max': datetime.now().year}),
        }

    def clean_name(self):
        name = self.cleaned_data.get('name').strip()
        # Exclude current instance when updating
        queryset = Publisher.objects.filter(name__iexact=name)
        if self.instance and self.instance.pk:
            queryset = queryset.exclude(pk=self.instance.pk)
        if queryset.exists():
            raise forms.ValidationError("Publisher with this name already exists.")
        return name

# ---------------------- Member Form (with linked User) ----------------------
class MemberForm(forms.ModelForm):
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))

    class Meta:
        model = Member
        fields = ['member_id', 'phone', 'address', 'role']
        widgets = {
            'member_id': forms.TextInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and self.instance.user:
            self.fields['first_name'].initial = self.instance.user.first_name
            self.fields['last_name'].initial = self.instance.user.last_name
            self.fields['email'].initial = self.instance.user.email

    def save(self, commit=True):
        member = super().save(commit=False)
        if self.instance and self.instance.user:
            # Update the associated User model
            user = self.instance.user
            user.first_name = self.cleaned_data['first_name']
            user.last_name = self.cleaned_data['last_name']
            user.email = self.cleaned_data['email']
            if commit:
                user.save()
        if commit:
            member.save()
        return member

# ---------------------- Member Update Form ----------------------
class MemberUpdateForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['phone', 'address']
        widgets = {
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

# ---------------------- User Registration Form ----------------------
class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password1', 'password2']
        widgets = {'username': forms.TextInput(attrs={'class': 'form-control'})}

# ---------------------- User Update Form ----------------------
class UserUpdateForm(UserChangeForm):
    email = forms.EmailField(required=True, widget=forms.EmailInput(attrs={'class': 'form-control'}))
    first_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
    last_name = forms.CharField(max_length=30, required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop('password', None)

# ---------------------- BorrowRecord Form ----------------------
class BorrowRecordForm(forms.ModelForm):
    member = forms.ModelChoiceField(queryset=None, widget=forms.Select(attrs={'class': 'form-select'}))

    class Meta:
        model = BorrowRecord
        fields = ['member', 'due_date']
        widgets = {
            'due_date': forms.DateTimeInput(attrs={'type': 'datetime-local', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['member'].queryset = Member.objects.filter(is_active=True)
        # Set default due date to 14 days from now
        from django.utils import timezone
        from datetime import timedelta
        if not self.instance.pk:  # Only for new records
            self.fields['due_date'].initial = timezone.now() + timedelta(days=14)


# ---------------------- Book Form ----------------------
class BookForm(forms.ModelForm):
    authors = forms.ModelMultipleChoiceField(
        queryset=Author.objects.none(),
        required=False,
        widget=forms.CheckboxSelectMultiple(),
        help_text="Select existing authors"
    )
    publisher = forms.ModelChoiceField(
        queryset=Publisher.objects.none(),
        required=False,
        widget=forms.Select(attrs={'class': 'form-select'}),
        help_text="Select existing publisher"
    )
    new_authors = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Author1, Author2'}),
        help_text="Enter multiple authors separated by commas"
    )
    new_publisher = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Publisher name'}),
        help_text="Create new publisher if not listed"
    )
    location_name = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter location'}),
        label="Location"
    )

    class Meta:
        model = Book
        fields = [
            'title', 'subtitle', 'isbn', 'published_date', 'edition', 'volume',
            'book_type', 'page_count', 'description', 'cover_image',
            'acquisition_price', 'available_copies', 'categories'
        ]
        widgets = {
            'title': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Book title'}),
            'subtitle': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subtitle'}),
            'isbn': forms.TextInput(attrs={'class': 'form-control'}),
            'published_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'edition': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'volume': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'book_type': forms.Select(attrs={'class': 'form-select'}),
            'page_count': forms.NumberInput(attrs={'class': 'form-control', 'min': 1}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'cover_image': forms.FileInput(attrs={'class': 'form-control', 'accept': 'image/*'}),
            'acquisition_price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'available_copies': forms.NumberInput(attrs={'class': 'form-control', 'min': 0}),
            'categories': forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['authors'].queryset = Author.objects.all().order_by('name')
        self.fields['publisher'].queryset = Publisher.objects.all().order_by('name')
        self.fields['categories'].queryset = Category.objects.filter(is_active=True).order_by('name')
        if self.instance and self.instance.location:
            self.fields['location_name'].initial = self.instance.location.name
        # Set initial values for existing authors and publisher
        if self.instance and self.instance.pk:
            self.fields['authors'].initial = [author.pk for author in self.instance.authors.all()]
            self.fields['publisher'].initial = self.instance.publisher.pk if self.instance.publisher else None

    def save(self, commit=True):
        book = super().save(commit=False)
        loc_name = self.cleaned_data.get('location_name')
        if loc_name:
            location, created = Location.objects.get_or_create(name=loc_name)
            book.location = location

        if commit:
            book.save()
            self.save_m2m()
        return book
