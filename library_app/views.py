import csv
import json
from io import TextIOWrapper
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib import messages
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from django.contrib.auth.decorators import login_required

from .models import Book, Member, BorrowRecord, Category
from .forms import BookForm, CategoryForm, UserRegistrationForm
from .decorators import librarian_required


# ---------------------- Public Views ----------------------
def home(request):
    books = Book.objects.all()[:8]  # Show 8 recent books
    return render(request, 'library_app/home.html', {'books': books})


def book_list(request):
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    category_filter = request.GET.get('category', '')
    year_filter = request.GET.get('year', '')

    books = Book.objects.all()
    if query:
        books = books.filter(
            Q(title__icontains=query) |
            Q(authors__icontains=query) |
            Q(isbn__icontains=query)
        )
    if category_filter:
        books = books.filter(categories__id=category_filter)
    if status_filter:
        books = books.filter(status=status_filter)
    if year_filter:
        books = books.filter(published_date__year=year_filter)

    paginator = Paginator(books, 12)
    page_number = request.GET.get('page')
    try:
        books = paginator.page(page_number)
    except PageNotAnInteger:
        books = paginator.page(1)
    except EmptyPage:
        books = paginator.page(paginator.num_pages)

    categories = Category.objects.filter(is_active=True)
    status_choices = Book.STATUS_CHOICES

    context = {
        'books': books,
        'query': query,
        'status_filter': status_filter,
        'category_filter': category_filter,
        'year_filter': year_filter,
        'categories': categories,
        'status_choices': status_choices,
    }
    return render(request, 'library_app/book_list.html', context)


def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    return render(request, 'library_app/book_detail.html', {'book': book})


def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            Member.objects.create(user=user, member_id=f"STU{user.id:04d}")
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password1')
            user = authenticate(username=username, password=password)
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('home')
    else:
        form = UserRegistrationForm()
    return render(request, 'library_app/register.html', {'form': form})


# ---------------------- Librarian Views ----------------------
@login_required
@user_passes_test(librarian_required)
def dashboard(request):
    total_books = Book.objects.count()
    total_members = Member.objects.count()
    borrowed_books = BorrowRecord.objects.filter(return_date__isnull=True).count()
    overdue_books = BorrowRecord.objects.filter(return_date__isnull=True, due_date__lt=timezone.now()).count()

    context = {
        'total_books': total_books,
        'total_members': total_members,
        'borrowed_books': borrowed_books,
        'overdue_books': overdue_books,
    }
    return render(request, 'library_app/dashboard.html', context)


# ---------------------- Book CRUD ----------------------
@login_required
@user_passes_test(librarian_required)
def book_create(request):
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES)
        if form.is_valid():
            book = form.save(commit=False)
            book.created_by = request.user
            book.save()
            form.save_m2m()
            messages.success(request, 'Book added successfully!')
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm()
    categories = Category.objects.filter(is_active=True)
    return render(request, 'library_app/book_form.html', {'form': form, 'categories': categories, 'title': 'Add New Book'})


@login_required
@user_passes_test(librarian_required)
def book_update(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        form = BookForm(request.POST, request.FILES, instance=book)
        if form.is_valid():
            form.save()
            messages.success(request, 'Book updated successfully!')
            return redirect('book_detail', pk=book.pk)
    else:
        form = BookForm(instance=book)
    categories = Category.objects.filter(is_active=True)
    return render(request, 'library_app/book_form.html', {'form': form, 'categories': categories, 'title': 'Edit Book'})


@login_required
@user_passes_test(librarian_required)
def book_delete(request, pk):
    book = get_object_or_404(Book, pk=pk)
    if request.method == 'POST':
        book.delete()
        messages.success(request, 'Book deleted successfully!')
        return redirect('book_list')
    return render(request, 'library_app/book_confirm_delete.html', {'book': book})


# ---------------------- Borrow / Return ----------------------
@login_required
def borrow_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    if book.status == 'Available':
        BorrowRecord.objects.create(book=book, member=request.user.member)
        book.status = 'Borrowed'
        book.save()
        messages.success(request, f"You borrowed '{book.title}'.")
    else:
        messages.error(request, f"'{book.title}' is not available for borrowing.")
    return redirect('home')


@login_required
def return_book(request, book_id):
    book = get_object_or_404(Book, id=book_id)
    record = BorrowRecord.objects.filter(book=book, member=request.user.member, return_date__isnull=True).first()
    if record:
        record.return_date = timezone.now()
        record.save()
        book.status = 'Available'
        book.save()
        messages.success(request, f"You returned '{book.title}'.")
    else:
        messages.error(request, f"No active borrow record found for '{book.title}'.")
    return redirect('home')


# ---------------------- Member CRUD ----------------------
@login_required
@user_passes_test(librarian_required)
def member_list(request):
    members = Member.objects.all().order_by('id')
    paginator = Paginator(members, 12)
    page_number = request.GET.get('page')
    try:
        members = paginator.page(page_number)
    except PageNotAnInteger:
        members = paginator.page(1)
    except EmptyPage:
        members = paginator.page(paginator.num_pages)
    return render(request, 'library_app/member_list.html', {'members': members})


@login_required
@user_passes_test(librarian_required)
def member_detail(request, pk):
    member = get_object_or_404(Member, pk=pk)
    return render(request, 'library_app/member_detail.html', {'member': member})


@login_required
@user_passes_test(librarian_required)
def member_edit(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST, instance=member.user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Member updated successfully!')
            return redirect('member_detail', pk=pk)
    else:
        form = UserRegistrationForm(instance=member.user)
    return render(request, 'library_app/member_form.html', {'form': form})


@login_required
@user_passes_test(librarian_required)
def member_delete(request, pk):
    member = get_object_or_404(Member, pk=pk)
    if request.method == 'POST':
        member.user.delete()
        member.delete()
        messages.success(request, 'Member deleted successfully!')
        return redirect('member_list')
    return render(request, 'library_app/member_confirm_delete.html', {'member': member})


# ---------------------- Category Management ----------------------
class CategoryListView(ListView):
    model = Category
    template_name = 'library_app/category_list.html'
    context_object_name = 'categories'

    def get_queryset(self):
        return Category.objects.filter(is_active=True).order_by('name')


class CategoryCreateView(CreateView):
    model = Category
    form_class = CategoryForm
    template_name = 'library_app/category_form.html'
    success_url = reverse_lazy('category_list')


class CategoryUpdateView(UpdateView):
    model = Category
    form_class = CategoryForm
    template_name = 'library_app/category_form.html'
    success_url = reverse_lazy('category_list')


class CategoryDeleteView(DeleteView):
    model = Category
    template_name = 'library_app/category_confirm_delete.html'
    success_url = reverse_lazy('category_list')

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        self.object.is_active = False
        self.object.save()
        return JsonResponse({'success': True})


def get_categories_json(request):
    categories = Category.objects.filter(is_active=True).values('id', 'name', 'color')
    return JsonResponse(list(categories), safe=False)
@login_required
def profile_view(request):
    # You can pass user data if needed
    return render(request, 'library_app/profile.html', {'user': request.user})
