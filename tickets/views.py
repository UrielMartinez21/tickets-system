"""Vistas de la app tickets: CRUD y flujo de estados con control por rol."""
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.db.models import Q
from django.shortcuts import get_object_or_404, redirect, render

from accounts import roles

from .forms import (
    AsignarAgenteForm,
    CambiarEstadoForm,
    ComentarioForm,
    TicketForm,
)
from .models import Estado, Prioridad, TransicionInvalidaError


def _tickets_visibles(user):
    """Devuelve el queryset de tickets que el usuario puede ver.

    - Admin/Agente: todos los tickets.
    - Solicitante: solo los que creó.
    """
    from .models import Ticket

    if roles.es_staff_tickets(user):
        return Ticket.objects.all()
    return Ticket.objects.filter(solicitante=user)


@login_required
def lista_tickets(request):
    """Listado de tickets con filtros por estado y prioridad."""
    tickets = _tickets_visibles(request.user).select_related(
        "solicitante", "agente"
    )

    estado = request.GET.get("estado")
    prioridad = request.GET.get("prioridad")
    buscar = request.GET.get("q")

    if estado:
        tickets = tickets.filter(estado=estado)
    if prioridad:
        tickets = tickets.filter(prioridad=prioridad)
    if buscar:
        tickets = tickets.filter(
            Q(titulo__icontains=buscar) | Q(descripcion__icontains=buscar)
        )

    contexto = {
        "tickets": tickets,
        "estados": Estado.choices,
        "prioridades": Prioridad.choices,
        "filtro_estado": estado or "",
        "filtro_prioridad": prioridad or "",
        "busqueda": buscar or "",
    }
    return render(request, "tickets/lista.html", contexto)


@login_required
def crear_ticket(request):
    """Crea un ticket. El solicitante es el usuario autenticado."""
    if request.method == "POST":
        form = TicketForm(request.POST)
        if form.is_valid():
            ticket = form.save(commit=False)
            ticket.solicitante = request.user
            ticket.save()
            messages.success(request, f"Ticket #{ticket.pk} creado.")
            return redirect("tickets:detalle", pk=ticket.pk)
    else:
        form = TicketForm()
    return render(request, "tickets/crear.html", {"form": form})


@login_required
def detalle_ticket(request, pk):
    """Detalle del ticket con comentarios y acciones según rol."""
    ticket = get_object_or_404(
        _tickets_visibles(request.user).select_related("solicitante", "agente"),
        pk=pk,
    )

    comentario_form = ComentarioForm()
    estado_form = CambiarEstadoForm(ticket=ticket)
    agente_form = AsignarAgenteForm(instance=ticket)

    contexto = {
        "ticket": ticket,
        "comentarios": ticket.comentarios.select_related("autor"),
        "comentario_form": comentario_form,
        "estado_form": estado_form,
        "agente_form": agente_form,
        "puede_gestionar": roles.es_staff_tickets(request.user),
    }
    return render(request, "tickets/detalle.html", contexto)


@login_required
def agregar_comentario(request, pk):
    """Agrega un comentario al ticket."""
    ticket = get_object_or_404(_tickets_visibles(request.user), pk=pk)
    if request.method == "POST":
        form = ComentarioForm(request.POST)
        if form.is_valid():
            comentario = form.save(commit=False)
            comentario.ticket = ticket
            comentario.autor = request.user
            comentario.save()
            messages.success(request, "Comentario agregado.")
    return redirect("tickets:detalle", pk=ticket.pk)


@login_required
def cambiar_estado(request, pk):
    """Cambia el estado del ticket. Solo Admin/Agente."""
    if not roles.es_staff_tickets(request.user):
        raise PermissionDenied("Solo Admin o Agente pueden cambiar el estado.")

    from .models import Ticket

    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == "POST":
        form = CambiarEstadoForm(request.POST, ticket=ticket)
        if form.is_valid():
            try:
                ticket.cambiar_estado(form.cleaned_data["nuevo_estado"])
                messages.success(
                    request,
                    f"Estado actualizado a '{ticket.get_estado_display()}'.",
                )
            except TransicionInvalidaError as exc:
                messages.error(request, "; ".join(exc.messages))
        else:
            messages.error(request, "Estado no válido.")
    return redirect("tickets:detalle", pk=ticket.pk)


@login_required
def asignar_agente(request, pk):
    """Asigna un agente al ticket. Solo Admin/Agente."""
    if not roles.es_staff_tickets(request.user):
        raise PermissionDenied("Solo Admin o Agente pueden asignar.")

    from .models import Ticket

    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == "POST":
        form = AsignarAgenteForm(request.POST, instance=ticket)
        if form.is_valid():
            form.save()
            messages.success(request, "Agente asignado.")
        else:
            messages.error(request, "No se pudo asignar el agente.")
    return redirect("tickets:detalle", pk=ticket.pk)


@login_required
def autoasignarme(request, pk):
    """Permite a un Agente/Admin autoasignarse el ticket."""
    if not roles.es_staff_tickets(request.user):
        raise PermissionDenied("Solo Admin o Agente pueden autoasignarse.")

    from .models import Ticket

    ticket = get_object_or_404(Ticket, pk=pk)
    if request.method == "POST":
        ticket.agente = request.user
        ticket.save(update_fields=["agente"])
        messages.success(request, "Te has asignado este ticket.")
    return redirect("tickets:detalle", pk=ticket.pk)
