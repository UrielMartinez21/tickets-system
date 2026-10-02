"""Context processors de la app accounts.

Expone información de roles a todas las plantillas, para mostrar/ocultar
elementos de la UI según el rol del usuario autenticado.
"""
from . import roles as _roles


def roles(request):
    """Agrega banderas de rol al contexto de las plantillas."""
    user = request.user
    return {
        "es_admin": _roles.es_admin(user),
        "es_agente": _roles.es_agente(user),
        "es_solicitante": _roles.es_solicitante(user),
        "es_staff_tickets": _roles.es_staff_tickets(user),
    }
