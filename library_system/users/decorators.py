from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import login_required
from functools import wraps

def librarian_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_required(view_func)(request, *args, **kwargs)
        if not hasattr(request.user, 'is_librarian') or not request.user.is_librarian():
            return HttpResponseForbidden("Доступ запрещен. Требуются права библиотекаря.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def admin_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_required(view_func)(request, *args, **kwargs)
        if not hasattr(request.user, 'is_admin') or not request.user.is_admin():
            return HttpResponseForbidden("Доступ запрещен. Требуются права администратора.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def reader_required(view_func):
    """Только для читателей (не библиотекарей и администраторов)"""
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return login_required(view_func)(request, *args, **kwargs)
        if request.user.is_librarian() or request.user.is_admin():
            return HttpResponseForbidden("Доступ запрещен. Эта страница только для читателей.")
        return view_func(request, *args, **kwargs)
    return _wrapped_view


def role_required(allowed_roles):
    """Универсальный декоратор для проверки списка ролей"""
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return login_required(view_func)(request, *args, **kwargs)
            if request.user.role not in allowed_roles:
                return HttpResponseForbidden("Доступ запрещен. Недостаточно прав.")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator