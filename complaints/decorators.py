from functools import wraps

from django.contrib import messages
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect
from django.urls import reverse

from .constants import ROLE_ADMIN


def login_required(view):
    """Redirect anonymous visitors to the citizen login page."""
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in to continue.")
            return redirect_to_login(request.get_full_path(), reverse("login"))
        return view(request, *args, **kwargs)
    return wrapped


def admin_required(view):
    """Only administrators; citizens get 403, anonymous visitors get the admin login."""
    @wraps(view)
    def wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.warning(request, "Please log in as an administrator.")
            return redirect("admin_login")
        if request.user.role != ROLE_ADMIN:
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return wrapped
