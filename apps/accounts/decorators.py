from functools import wraps

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import redirect


def admin_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_platform_admin():
            messages.error(request, "You don't have permission to access that page.")
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return _wrapped


def school_required(view_func):
    @wraps(view_func)
    @login_required
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_school_admin() or request.user.school_id is None:
            messages.error(request, "You don't have permission to access that page.")
            return redirect('dashboard:index')
        return view_func(request, *args, **kwargs)
    return _wrapped
