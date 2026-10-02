"""Decoradores y mixins para control de acceso basado en roles (RBAC)."""
from functools import wraps

from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied

from . import roles


def _usuario_cumple(user, test_func):
    """Lanza PermissionDenied (403) si el usuario no pasa la prueba."""
    if not test_func(user):
        raise PermissionDenied(
            "No tienes permisos suficientes para acceder a esta sección."
        )


def admin_requerido(view_func):
    """Decorador: solo permite el acceso a usuarios del rol Admin."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        _usuario_cumple(request.user, roles.es_admin)
        return view_func(request, *args, **kwargs)

    return _wrapped


def staff_tickets_requerido(view_func):
    """Decorador: permite el acceso a Admin o Agente."""

    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        _usuario_cumple(request.user, roles.es_staff_tickets)
        return view_func(request, *args, **kwargs)

    return _wrapped


class AdminRequeridoMixin(UserPassesTestMixin):
    """Mixin para vistas basadas en clases: solo Admin."""

    def test_func(self):
        return roles.es_admin(self.request.user)

    def handle_no_permission(self):
        raise PermissionDenied(
            "No tienes permisos suficientes para acceder a esta sección."
        )


class StaffTicketsRequeridoMixin(UserPassesTestMixin):
    """Mixin para vistas basadas en clases: Admin o Agente."""

    def test_func(self):
        return roles.es_staff_tickets(self.request.user)

    def handle_no_permission(self):
        raise PermissionDenied(
            "No tienes permisos suficientes para acceder a esta sección."
        )
