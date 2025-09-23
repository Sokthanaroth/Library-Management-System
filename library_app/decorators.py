from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test

def librarian_required(view_func):
    """
    Decorator for views that checks that the user is a librarian (staff member),
    redirecting to the login page if necessary.
    """
    def check_librarian(user):
        return user.is_authenticated and user.is_staff
    
    return user_passes_test(check_librarian)(view_func)

def member_required(view_func):
    """
    Decorator for views that checks that the user is a library member,
    redirecting to the login page if necessary.
    """
    def check_member(user):
        return user.is_authenticated and hasattr(user, 'member')
    
    return user_passes_test(check_member)(view_func)