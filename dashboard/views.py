"""Vistas del dashboard de analítica y exportación a CSV."""
import csv

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.http import HttpResponse
from django.shortcuts import render
from django.utils import timezone

from accounts.permissions import staff_tickets_requerido
from tickets.models import Ticket

from . import metrics


@login_required
@staff_tickets_requerido
def index(request):
    """Dashboard principal con todas las métricas."""
    contexto = metrics.resumen_completo()
    return render(request, "dashboard/index.html", contexto)


def _respuesta_csv(nombre_archivo):
    """Crea una HttpResponse configurada para descargar un CSV."""
    response = HttpResponse(content_type="text/csv; charset=utf-8")
    response["Content-Disposition"] = (
        f'attachment; filename="{nombre_archivo}"'
    )
    # BOM para que Excel reconozca UTF-8 correctamente.
    response.write("\ufeff")
    return response


@login_required
@staff_tickets_requerido
def exportar_tickets_csv(request):
    """Exporta todos los tickets a CSV."""
    response = _respuesta_csv("tickets.csv")
    writer = csv.writer(response)
    writer.writerow(
        [
            "ID",
            "Título",
            "Estado",
            "Prioridad",
            "Solicitante",
            "Agente",
            "Creado",
            "Actualizado",
            "Resuelto en",
        ]
    )
    tickets = Ticket.objects.select_related("solicitante", "agente").all()
    for t in tickets:
        writer.writerow(
            [
                t.pk,
                t.titulo,
                t.get_estado_display(),
                t.get_prioridad_display(),
                t.solicitante.username if t.solicitante else "",
                t.agente.username if t.agente else "",
                timezone.localtime(t.creado).strftime("%Y-%m-%d %H:%M"),
                timezone.localtime(t.actualizado).strftime("%Y-%m-%d %H:%M"),
                timezone.localtime(t.resuelto_en).strftime("%Y-%m-%d %H:%M")
                if t.resuelto_en
                else "",
            ]
        )
    return response


@login_required
@staff_tickets_requerido
def exportar_usuarios_csv(request):
    """Exporta todos los usuarios a CSV."""
    response = _respuesta_csv("usuarios.csv")
    writer = csv.writer(response)
    writer.writerow(
        ["ID", "Usuario", "Nombre", "Correo", "Roles", "Activo", "Alta"]
    )
    usuarios = User.objects.prefetch_related("groups").all()
    for u in usuarios:
        roles_u = ", ".join(u.groups.values_list("name", flat=True))
        writer.writerow(
            [
                u.pk,
                u.username,
                u.get_full_name(),
                u.email,
                roles_u,
                "Sí" if u.is_active else "No",
                timezone.localtime(u.date_joined).strftime("%Y-%m-%d %H:%M"),
            ]
        )
    return response


@login_required
@staff_tickets_requerido
def exportar_metricas_csv(request):
    """Exporta el resumen de métricas a CSV."""
    datos = metrics.resumen_completo()
    response = _respuesta_csv("metricas.csv")
    writer = csv.writer(response)

    writer.writerow(["Métrica", "Valor"])
    writer.writerow(["Total de tickets", datos["total_tickets"]])
    writer.writerow(["Total de usuarios", datos["total_usuarios"]])
    writer.writerow(["Tickets abiertos", datos["abiertos"]])
    writer.writerow(["Tickets cerrados", datos["cerrados"]])
    writer.writerow(
        ["Tickets creados en últimos 30 días", datos["ultimos_30_dias"]]
    )
    writer.writerow(
        [
            "Tiempo promedio de resolución (horas)",
            datos["promedio_resolucion_horas"]
            if datos["promedio_resolucion_horas"] is not None
            else "N/A",
        ]
    )

    writer.writerow([])
    writer.writerow(["Estado", "Total"])
    for etiqueta, total in datos["por_estado"]:
        writer.writerow([etiqueta, total])

    writer.writerow([])
    writer.writerow(["Prioridad", "Total"])
    for etiqueta, total in datos["por_prioridad"]:
        writer.writerow([etiqueta, total])

    writer.writerow([])
    writer.writerow(["Rol", "Usuarios"])
    for rol, total in datos["usuarios_por_rol"]:
        writer.writerow([rol, total])

    writer.writerow([])
    writer.writerow(["Agente", "Tickets asignados"])
    for agente, total in datos["tickets_por_agente"]:
        writer.writerow([agente, total])

    return response
