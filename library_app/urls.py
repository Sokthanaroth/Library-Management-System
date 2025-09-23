from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Home
    path('', views.home, name='home'),

    # Books
    path('books/', views.book_list, name='book_list'),
    path('books/add/', views.book_create, name='book_create'),
    path('books/<int:pk>/', views.book_detail, name='book_detail'),
    path('books/<int:pk>/edit/', views.book_update, name='book_update'),
    path('books/<int:pk>/delete/', views.book_delete, name='book_delete'),

    # Borrow / Return
    path('books/<int:book_id>/borrow/', views.borrow_book, name='borrow_book'),
    path('books/<int:book_id>/return/', views.return_book, name='return_book'),
    
    # Members
    path('members/', views.member_list, name='member_list'),
    path('members/add/', views.register, name='member_create'),
    path('members/<int:pk>/', views.member_detail, name='member_detail'),
    path('members/<int:pk>/edit/', views.member_edit, name='member_edit'),
    path('members/<int:pk>/delete/', views.member_delete, name='member_delete'),

    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),

    # Authentication
    path('login/', auth_views.LoginView.as_view(template_name='library_app/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    path('password-reset/', auth_views.PasswordResetView.as_view(template_name='library_app/password_reset_form.html'), name='password_reset'),
    path('password-reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='library_app/password_reset_done.html'), name='password_reset_done'),
    path('password-reset/confirm/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='library_app/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password-reset/complete/', auth_views.PasswordResetCompleteView.as_view(template_name='library_app/password_reset_complete.html'), name='password_reset_complete'),

    # Categories
    path('categories/', views.CategoryListView.as_view(), name='category_list'),
    path('categories/add/', views.CategoryCreateView.as_view(), name='category_create'),
    path('categories/<int:pk>/edit/', views.CategoryUpdateView.as_view(), name='category_update'),
    path('categories/<int:pk>/delete/', views.CategoryDeleteView.as_view(), name='category_delete'),
    path('api/categories/', views.get_categories_json, name='get_categories_json'),

# Profile
    path('profile/', views.profile_view, name='profile'),

    path('password-change/', auth_views.PasswordChangeView.as_view(template_name='library_app/change_password.html'), name='change_password'),
    path('password-change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='library_app/change_password_done.html'), name='password_change_done'),
]

