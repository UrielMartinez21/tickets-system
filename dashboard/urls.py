"""URLs de la app dashboard."""
from django.urls import path

from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.index, name="index"),
    path("exportar/tickets.csv", views.exportar_tickets_csv, name="exportar_tickets"),
    path(
        "exportar/usuarios.csv",
        views.exportar_usuarios_csv,
        name="exportar_usuarios",
    ),
    path(
        "exportar/metricas.csv",
        views.exportar_metricas_csv,
        name="exportar_metricas",
    ),
]
