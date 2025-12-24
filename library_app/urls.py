from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Dashboard (Librarian only)
    path('dashboard/', views.dashboard, name='dashboard'),

    # Books
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_create, name='book_create'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/edit/', views.book_update, name='book_update'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),
    path('books/<int:book_id>/borrow/', views.borrow_book, name='borrow_book'),
    path('borrow-form/<int:book_id>/', views.borrow_book, name='borrow_form'),
    # Barcode and Reports
    path('books/<int:book_id>/barcode/', views.generate_barcode, name='generate_barcode'),
    path('print-barcodes/', views.print_barcodes, name='print_barcodes'),
    path('reports/', views.generate_report, name='generate_report'),

    # Barcode Scanner
    path('barcode-scanner/', views.barcode_scanner, name='barcode_scanner'),
    path('scan-barcode/', views.scan_barcode, name='scan_barcode'),
    path('bulk-scan/', views.bulk_scan, name='bulk_scan'),

    path('borrow-records/', views.borrow_records_list, name='borrow_records'),
    path('borrow-records/<int:borrow_id>/return/', views.return_book, name='return_book'),

    # Authors
    path('authors/', views.author_list, name='author_list'),
    path('authors/add/', views.author_create, name='author_create'),
    path('authors/<int:pk>/', views.author_detail, name='author_detail'),
    path('authors/<int:pk>/edit/', views.author_update, name='author_update'),
    path('authors/<int:pk>/delete/', views.author_delete, name='author_delete'),

    # Publishers
    path('publishers/', views.publisher_list, name='publisher_list'),
    path('publishers/add/', views.publisher_create, name='publisher_create'),
    path('publishers/<int:pk>/', views.publisher_detail, name='publisher_detail'),
    path('publishers/<int:pk>/edit/', views.publisher_update, name='publisher_update'),
    path('publishers/<int:pk>/delete/', views.publisher_delete, name='publisher_delete'),

    # Members
    path('members/', views.member_list, name='member_list'),
    path('members/add/', views.register, name='member_create'),  # public registration
    path('members/create/', views.member_create, name='member_create_staff'),  # staff member creation
    path('users/create/', views.user_create, name='user_create'),  # admin user creation
    path('members/<int:pk>/', views.member_detail, name='member_detail'),
    path('members/<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('members/<int:pk>/delete/', views.member_delete, name='member_delete'),
    path('members/<int:member_id>/topup/', views.member_topup, name='member_topup'),
    path('members/<int:member_id>/barcode/', views.generate_barcode, name='generate_member_barcode'),
    path('members/<int:member_id>/card/', views.generate_library_card, name='generate_library_card'),

    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/<int:pk>/', views.category_detail, name='category_detail'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('api/categories/', views.get_categories_json, name='get_categories_json'),

    # Profile
    path('profile/', views.profile_view, name='profile'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='library_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('register/', views.register, name='register'),

    # Password Reset
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='library_app/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='library_app/password_reset_done.html'), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='library_app/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='library_app/password_reset_complete.html'), name='password_reset_complete'),

    # Password Change
    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='library_app/change_password.html'), name='change_password'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='library_app/change_password_done.html'), name='password_change_done'),
]
