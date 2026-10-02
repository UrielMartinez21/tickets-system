"""Registro de modelos de tickets en el admin de Django."""
from django.contrib import admin

from .models import Comentario, Ticket


class ComentarioInline(admin.TabularInline):
    model = Comentario
    extra = 0
    readonly_fields = ("autor", "creado")


@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "titulo",
        "estado",
        "prioridad",
        "solicitante",
        "agente",
        "creado",
    )
    list_filter = ("estado", "prioridad", "creado")
    search_fields = ("titulo", "descripcion")
    date_hierarchy = "creado"
    inlines = [ComentarioInline]


@admin.register(Comentario)
class ComentarioAdmin(admin.ModelAdmin):
    list_display = ("id", "ticket", "autor", "creado")
    search_fields = ("texto",)
