from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db.models import Q
from django.utils import timezone
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.generic import ListView, CreateView, UpdateView, DeleteView
from .forms import UserUpdateForm, MemberUpdateForm
from .models import Book, Member, BorrowRecord, Category, Author, Publisher
from .forms import (
    BookForm, CategoryForm, MemberForm, UserRegistrationForm,
    UserUpdateForm, AuthorForm, PublisherForm
)
from .decorators import librarian_required
from django.contrib.auth import authenticate, login, logout

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
    query = request.GET.get('q', '')
    status_filter = request.GET.get('status', '')
    role_filter = request.GET.get('role', '')

    members = Member.objects.all().order_by('id')

    if query:
        members = members.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(user__email__icontains=query)
        )
    if status_filter:
        if status_filter == 'active':
            members = members.filter(is_active=True)
        elif status_filter == 'inactive':
            members = members.filter(is_active=False)

    if role_filter:
        members = members.filter(role=role_filter)

    paginator = Paginator(members, 12)
    page_number = request.GET.get('page')
    try:
        members = paginator.page(page_number)
    except PageNotAnInteger:
        members = paginator.page(1)
    except EmptyPage:
        members = paginator.page(paginator.num_pages)

    context = {
        'members': members,
        'query': query,
        'status_filter': status_filter,
        'role_filter': role_filter,
    }
    return render(request, 'library_app/member_list.html', context)



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
        user_form = UserUpdateForm(request.POST, instance=member.user)
        member_form = MemberForm(request.POST, instance=member)

        if user_form.is_valid() and member_form.is_valid():
            user_form.save()
            member_obj = member_form.save(commit=False)
            member_obj.role = request.POST.get('role')
            member_obj.save()
            messages.success(request, 'Member updated successfully!')
            return redirect('member_detail', pk=member.pk)
        else:
            # Add this to debug errors
            print(user_form.errors, member_form.errors)

    else:
        user_form = UserUpdateForm(instance=member.user)
        member_form = MemberForm(instance=member)

    return render(request, 'library_app/member_form.html', {
        'user_form': user_form,
        'member_form': member_form,
        'title': 'Edit Member'
    })


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
    user = request.user
    # Ensure a Member exists for this user
    member, created = Member.objects.get_or_create(
        user=user,
        defaults={'member_id': f"M{user.id:04d}"}
    )

    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=user)
        member_form = MemberUpdateForm(request.POST, instance=member)

        if user_form.is_valid() and member_form.is_valid():
            user_form.save()
            member_form.save()
            messages.success(request, "Profile updated successfully!")
            return redirect('profile')
        else:
            messages.error(request, "Please fix the errors below.")
    else:
        user_form = UserUpdateForm(instance=user)
        member_form = MemberUpdateForm(instance=member)

    context = {
        'user_form': user_form,
        'member_form': member_form,
        'member': member,
    }
    return render(request, 'library_app/profile.html', context)

# ---------------------- Author CRUD ----------------------

@login_required
@user_passes_test(librarian_required)
def author_list(request):
    authors = Author.objects.all().order_by('name')
    query = request.GET.get('q', '')
    if query:
        authors = authors.filter(name__icontains=query)
    return render(request, 'library_app/author_list.html', {'authors': authors, 'query': query})

@login_required
@user_passes_test(librarian_required)
def author_detail(request, pk):
    author = get_object_or_404(Author, pk=pk)
    return render(request, 'library_app/author_detail.html', {'author': author})

@login_required
@user_passes_test(librarian_required)
def author_create(request):
    if request.method == 'POST':
        form = AuthorForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Author added successfully!')
            return redirect('author_list')
    else:
        form = AuthorForm()
    return render(request, 'library_app/author_form.html', {'form': form, 'title': 'Add Author'})

@login_required
@user_passes_test(librarian_required)
def author_update(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        form = AuthorForm(request.POST, instance=author)
        if form.is_valid():
            form.save()
            messages.success(request, 'Author updated successfully!')
            return redirect('author_detail', pk=author.pk)
    else:
        form = AuthorForm(instance=author)
    return render(request, 'library_app/author_form.html', {'form': form, 'title': 'Edit Author'})

@login_required
@user_passes_test(librarian_required)
def author_delete(request, pk):
    author = get_object_or_404(Author, pk=pk)
    if request.method == 'POST':
        author.delete()
        messages.success(request, 'Author deleted successfully!')
        return redirect('author_list')
    return render(request, 'library_app/author_confirm_delete.html', {'author': author})

# ---------------------- Publisher CRUD ----------------------

@login_required
@user_passes_test(librarian_required)
def publisher_list(request):
    query = request.GET.get('q', '')
    publishers = Publisher.objects.all().order_by('name')
    if query:
        publishers = publishers.filter(name__icontains=query)
    return render(request, 'library_app/publisher_list.html', {'publishers': publishers, 'query': query})

@login_required
@user_passes_test(librarian_required)
def publisher_detail(request, pk):
    publisher = get_object_or_404(Publisher, pk=pk)
    return render(request, 'library_app/publisher_detail.html', {'publisher': publisher})

@login_required
@user_passes_test(librarian_required)
def publisher_create(request):
    if request.method == 'POST':
        form = PublisherForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publisher added successfully!')
            return redirect('publisher_list')
        else:
            messages.error(request, 'Please correct the errors below.')
    else:
        form = PublisherForm()

    return render(request, 'library_app/publisher_form.html', {
        'form': form,
        'title': 'Add Publisher'
    })



@login_required
@user_passes_test(librarian_required)
def publisher_update(request, pk):
    publisher = get_object_or_404(Publisher, pk=pk)
    if request.method == 'POST':
        form = PublisherForm(request.POST, instance=publisher)
        if form.is_valid():
            form.save()
            messages.success(request, 'Publisher updated successfully!')
            return redirect('publisher_detail', pk=publisher.pk)
    else:
        form = PublisherForm(instance=publisher)
    return render(request, 'library_app/publisher_form.html', {'form': form, 'title': 'Edit Publisher'})

@login_required
@user_passes_test(librarian_required)
def publisher_delete(request, pk):
    publisher = get_object_or_404(Publisher, pk=pk)
    if request.method == 'POST':
        publisher.delete()
        messages.success(request, 'Publisher deleted successfully!')
        return redirect('publisher_list')
    return render(request, 'library_app/publisher_confirm_delete.html', {'publisher': publisher})