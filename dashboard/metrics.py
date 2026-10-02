"""Cálculo de métricas de analítica para el dashboard.

Se separa la lógica de agregación de las vistas para poder probarla
de forma aislada y reutilizarla en la exportación CSV.
"""
from datetime import timedelta

from django.contrib.auth.models import User
from django.db.models import Avg, Count, DurationField, ExpressionWrapper, F
from django.utils import timezone

from tickets.models import ESTADOS_CERRADOS, Estado, Prioridad, Ticket


def totales_por_estado():
    """Devuelve una lista [(etiqueta_estado, total)] para todos los estados."""
    conteo = dict(
        Ticket.objects.values_list("estado")
        .annotate(total=Count("id"))
        .values_list("estado", "total")
    )
    return [
        (Estado(valor).label, conteo.get(valor, 0)) for valor, _ in Estado.choices
    ]


def totales_por_prioridad():
    """Devuelve una lista [(etiqueta_prioridad, total)]."""
    conteo = dict(
        Ticket.objects.values_list("prioridad")
        .annotate(total=Count("id"))
        .values_list("prioridad", "total")
    )
    return [
        (Prioridad(valor).label, conteo.get(valor, 0))
        for valor, _ in Prioridad.choices
    ]


def usuarios_por_rol():
    """Devuelve [(nombre_rol, total_usuarios)]."""
    from django.contrib.auth.models import Group

    filas = (
        Group.objects.annotate(total=Count("user"))
        .order_by("name")
        .values_list("name", "total")
    )
    return list(filas)


def tickets_por_agente():
    """Devuelve [(nombre_agente, total_tickets)] para tickets asignados."""
    filas = (
        Ticket.objects.filter(agente__isnull=False)
        .values("agente__username")
        .annotate(total=Count("id"))
        .order_by("-total")
    )
    return [(f["agente__username"], f["total"]) for f in filas]


def tickets_ultimos_30_dias():
    """Número de tickets creados en los últimos 30 días."""
    desde = timezone.now() - timedelta(days=30)
    return Ticket.objects.filter(creado__gte=desde).count()


def tiempo_promedio_resolucion_horas():
    """Tiempo promedio de resolución en horas (tickets resueltos).

    Devuelve None si no hay tickets resueltos.
    """
    duracion = ExpressionWrapper(
        F("resuelto_en") - F("creado"), output_field=DurationField()
    )
    resultado = (
        Ticket.objects.filter(
            estado=Estado.RESUELTO, resuelto_en__isnull=False
        )
        .annotate(duracion=duracion)
        .aggregate(promedio=Avg("duracion"))
    )
    promedio = resultado["promedio"]
    if promedio is None:
        return None
    return round(promedio.total_seconds() / 3600, 1)


def abiertos_vs_cerrados():
    """Devuelve un dict con el conteo de tickets abiertos y cerrados."""
    cerrados = Ticket.objects.filter(estado__in=ESTADOS_CERRADOS).count()
    total = Ticket.objects.count()
    return {"abiertos": total - cerrados, "cerrados": cerrados}


def resumen_completo():
    """Agrega todas las métricas en un solo diccionario."""
    conteo_ac = abiertos_vs_cerrados()
    return {
        "total_tickets": Ticket.objects.count(),
        "total_usuarios": User.objects.count(),
        "por_estado": totales_por_estado(),
        "por_prioridad": totales_por_prioridad(),
        "usuarios_por_rol": usuarios_por_rol(),
        "tickets_por_agente": tickets_por_agente(),
        "ultimos_30_dias": tickets_ultimos_30_dias(),
        "promedio_resolucion_horas": tiempo_promedio_resolucion_horas(),
        "abiertos": conteo_ac["abiertos"],
        "cerrados": conteo_ac["cerrados"],
    }
