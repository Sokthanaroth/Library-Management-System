# library_app/decorators.py
from functools import wraps
from django.http import HttpResponseForbidden
from django.shortcuts import redirect

# ---------------------- Admin Decorator ----------------------
def admin_required(view_func):
    """
    Allows only superusers (full admin).
    Redirects to 'home' if not allowed.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and user.is_superuser:
            return view_func(request, *args, **kwargs)
        return redirect('home')  # Or use HttpResponseForbidden
    return _wrapped_view

# ---------------------- Staff / Librarian Decorator ----------------------
def staff_required(view_func):
    """
    Allows staff or superusers.
    Redirects to 'home' if not allowed.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return view_func(request, *args, **kwargs)
        return redirect('home')  # Or use HttpResponseForbidden
    return _wrapped_view

# ---------------------- Librarian / Staff with 403 ----------------------
def librarian_required(view_func):
    """
    Staff or superuser with 403 Forbidden response.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and (user.is_staff or user.is_superuser):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("You do not have permission to access this page.")
    return _wrapped_view

# ---------------------- Member Decorator ----------------------
def member_required(view_func):
    """
    Only library members (users with Member profile) can access.
    """
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        user = request.user
        if user.is_authenticated and hasattr(user, 'member'):
            return view_func(request, *args, **kwargs)
        return HttpResponseForbidden("You must be a library member to access this page.")
    return _wrapped_view
