"""Definición central de roles del sistema.

Los roles se implementan como grupos de Django (django.contrib.auth.Group).
Mantener los nombres aquí centralizados evita errores de "strings mágicos"
repartidos por el código.
"""

ROL_ADMIN = "Admin"
ROL_AGENTE = "Agente"
ROL_SOLICITANTE = "Solicitante"

ROLES = (ROL_ADMIN, ROL_AGENTE, ROL_SOLICITANTE)

# Roles que pueden gestionar tickets de otros (cambiar estado, asignarse, etc.)
ROLES_STAFF = (ROL_ADMIN, ROL_AGENTE)


def nombres_roles_usuario(user):
    """Devuelve el conjunto de nombres de rol (grupos) de un usuario."""
    if not user.is_authenticated:
        return set()
    return set(user.groups.values_list("name", flat=True))


def es_admin(user):
    """True si el usuario es superusuario o pertenece al grupo Admin."""
    if not user.is_authenticated:
        return False
    return user.is_superuser or user.groups.filter(name=ROL_ADMIN).exists()


def es_staff_tickets(user):
    """True si el usuario puede gestionar tickets (Admin o Agente)."""
    if not user.is_authenticated:
        return False
    if user.is_superuser:
        return True
    return user.groups.filter(name__in=ROLES_STAFF).exists()


def es_agente(user):
    """True si el usuario pertenece al grupo Agente."""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=ROL_AGENTE).exists()


def es_solicitante(user):
    """True si el usuario pertenece al grupo Solicitante."""
    if not user.is_authenticated:
        return False
    return user.groups.filter(name=ROL_SOLICITANTE).exists()
